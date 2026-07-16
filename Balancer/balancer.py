import random
from flask import (Flask,jsonify,request)
import requests as rq
from urllib.parse import urljoin
import subprocess
import time
from threading import Lock
import threading


CONTAINER_NO=3
SLOT_NO=512
VIRTUAL_PER_CONTAINER=9
def make_request(url,path):
    try:
        res=rq.request('GET',url=urljoin(url,path))
        print(res)
        if(res.status_code==200):
            print("request successful")
            return (res.json()["message"]),True
        else:
            return (f"request terminated with code {res.status_code}"),False
    except rq.ConnectionError:
        return "could not make connection to the server" ,False   
    
def gen_request_hash(i):
    return i^2+2*i+17
def gen_server_hash(i,j):
    return (i * 97 + j * 131 + 25) % 512
# to allow for multithreading 
ring_lock = Lock()

server_stats={}
class ring:
    def __init__(self,start=True,server_no=CONTAINER_NO):
        self.slots=[]  # hold actual slots including virtual servers
        self.lookUp={}
        self.servers_added=0
        for i in range (0,SLOT_NO):
            self.slots.append(None)
        # create initial 3 containers on on init
        for i in range(0,server_no):
            nServer=f"server_{self.servers_added+1}"
            subprocess.run(["docker","run","-d",
                            "--name",nServer,
                            "--network","net1",
                            "--network-alias",nServer,
                            "-e",f"SERVER_ID={self.servers_added+1}",
                            "default_server"],)
            url=f"http://{nServer}:5000"
            rounds=0
            while rounds<10:
                                    message, success=make_request(url,"/heartbeat")
                                    if not success:
                                        time.sleep(0.2)
                                        rounds+=1
                                        continue
                                    else:
                                        break
            if not success:
                                    subprocess.run(["docker","rm","-f",f"{nServer}"])
                                    print("error adding new conatainer instance")        
                                
            res=self.addServer(nServer,url)
            if not res:
                      print("error addingserver to keyring ")   
         
    def addServer(self,name,url):
        count=len(self.lookUp.keys())
        if(count>=(SLOT_NO/VIRTUAL_PER_CONTAINER)):
            return False
        if(name not in self.lookUp.keys()):
            self.lookUp[name]=[]
            self.servers_added+=1
        else:
            print("server already exists")
            return False   
        count=self.servers_added
        server_stats[name] = {
    "requests": 0,
    "status": "active"
}
        for a in range(0,VIRTUAL_PER_CONTAINER):
            j=a
            s_hash=gen_server_hash(count,j)
            slot=s_hash%SLOT_NO
            while True:
                if(self.slots[slot]!=None):
                    slot=(slot+1)%SLOT_NO;
                    continue
                else:
                    self.slots[slot]=({"name":name,"url":url,"id":count,"v_id":j})
                    self.lookUp[name].append(slot)
                    break
        return True
    def removeServer(self,name):
        for val in self.lookUp[name]:
            self.slots[val]=None
        self.lookUp.pop(name)
        server_stats[name]["status"] = "removed"
        return True
    def allocateRequest(self,r=None):
        if r==None:
            r=random.randint(0,999999)
        else:
            r=r
        r_index=gen_request_hash(r)%SLOT_NO
        s_index=r_index
        if(len(nRing.lookUp)<=0):
            print("empty ring no servers to allocate")
            return False
        count=0
        while True:
            if(count>=512):
                print("looped around entire ring no slots found")
                return False
            if(self.slots[s_index]==None):
                s_index=(s_index+1)%SLOT_NO
                count+=1
            else:
                server_stats[self.slots[s_index]["name"]]["requests"] += 1
                return self.slots[s_index]

    def monitor(self):
          while True:
            for server in list(nRing.lookUp.keys()):
               url=f"http://{server}:5000"
               message,success=make_request(url,"/heartbeat")
               if not success:
                   with ring_lock:
                    self.removeServer(name=server)
                   subprocess.run(["docker","rm","-f",f"{server}"])
                   nServer=f"server_{self.servers_added+1}"
                   subprocess.run(["docker","run","-d",
                            "--name",nServer,
                            "--network","net1",
                            "--network-alias",nServer,
                            "-e",f"SERVER_ID={self.servers_added+1}",
                            "default_server"],)
                   url=f"http://{nServer}:5000"
                   rounds=0
                   while rounds<10:
                                    message, success=make_request(url,"/heartbeat")
                                    if not success:
                                        time.sleep(0.2)
                                        rounds+=1
                                        continue
                                    else:
                                        break
                   if not success:
                                    subprocess.run(["docker","rm","-f",f"{nServer}"])
                                    print("error adding new conatainer instance")        
                   with ring_lock:         
                    res=self.addServer(nServer,url)
                    if not res:
                      print("error addingserver to keyring ")
                    
                    # add server if they are too few 
                   if len(self.lookUp.keys())<CONTAINER_NO:
                        for i in range (0,(CONTAINER_NO-len(self.lookUp.keys()))):
                            nServer=f"server_{self.servers_added+1}"
                            subprocess.run(["docker","run","-d",
                            "--name",nServer,
                            "--network","net1",
                            "--network-alias",nServer,
                            "-e",f"SERVER_ID={self.servers_added+1}",
                            "default_server"],)
                            url=f"http://{nServer}:5000"
                            rounds=0
                            while rounds<10:
                                    message, success=make_request(url,"/heartbeat")
                                    if not success:
                                        time.sleep(0.2)
                                        rounds+=1
                                        continue
                                    else:
                                        break
                            if not success:
                                    subprocess.run(["docker","rm","-f",f"{nServer}"])
                                    print("error adding new conatainer instance")        
                            with ring_lock: 
                                res=self.addServer(nServer,url)
                                if not res:
                                   print("error addingserver to keyring ")
                             

            time.sleep(5)
                   

nRing=ring()
app=Flask(__name__)
@app.route("/rep",methods=['GET'])
def get_status():
    number=len(nRing.lookUp)
    replicas=list(nRing.lookUp.keys())
    res=jsonify({"message":{"N":number,"replicas":replicas},"status":"successful"})
    return res,200
@app.route("/add",methods=['POST'])
def add_server():
    data=request.get_json()
    if not data:
        return jsonify({"message":"Error:payload empty or invalid"}),400
    n=data.get("n")
    count=nRing.servers_added
    def_name="server"
    names=[]
    if data.get("hostnames"):
        if(len(data.get("hostnames"))>n):
            return jsonify({"message":"Error:too many hostnames for intended no of instances"}),400
        names=data.get("hostnames")
    if(len(names)<n):
        for i in range (0,(n-len(names))):
            names.append(f"{def_name}_{count+i}")
    for i in range(0,n):
        # add code here to allow the docker file to create the container
        subprocess.run(["docker","run","-d",
                            "--name",names[i],
                            "--network","net1",
                            "--network-alias",names[i],
                            "-e",f"SERVER_ID={nRing.servers_added+1}",
                            "default_server"],)
        url=f"http://{names[i]}:5000"
        rounds=0
        while rounds<10:
            message, success=make_request(url,"/heartbeat")
            if not success:
                time.sleep(0.2)
                rounds+=1
                continue
            else:
                break
        if not success:
            subprocess.Popen(["docker","rm","-f",f"{names[i]}"])
            return jsonify({"message":f"Error:server {names[i]} failed to respond"}),500           
        with ring_lock:
            res=nRing.addServer(names[i],url)
            if not res:
                return jsonify({"message":"error appending to keyring"}),400
        
    return get_status()

@app.route("/rm",methods=['POST'])
def rm_server():
    data=request.get_json()
    if not data:
        return jsonify({"message":"Error:payload empty or invalid"}),400
    n=data.get("n")
    names=set()
    possible_names=set(nRing.lookUp.keys())
    if len(possible_names)<n:
       return jsonify({"message":"Error:active servers are fewer than expected deletions"}),400
    if data.get("hostnames"):
        if(len(data.get("hostnames"))>n):
            return jsonify({"message":"Error:too many hostnames for intended no of deletions"}),400
        names=set(data.get("hostnames"))
    if not all(val in possible_names for val in names):
        return jsonify({"message":"Error:invalid hostnames suggested"}),400
    valid_options=list(possible_names-names)
    if(n>len(names)):
        for i in range(0,(n-len(names))):
            index=random.choice(valid_options)
            names.add(index)
            valid_options.remove(index)
    # add code to allow actual stopping and deltion of containers 
    for name in names:
        subprocess.Popen(["docker","rm","-f",f"{name}"])
        with ring_lock:
            nRing.removeServer(name)
    return get_status()
@app.route("/<path>",methods=['GET'])
def foward_request(path):
    server=nRing.allocateRequest()
    if not server:
        return jsonify({"message":"no server to allocate to"}),400
    return make_request(server["url"],path)
@app.route("/statistics",methods=['GET'])
def get_statistics():
     if server_stats:
          return jsonify({"message":"statstics of all initializes servrs and their status","data":server_stats}),200

if __name__=="__main__":
    monitor_thread = threading.Thread(
    target=nRing.monitor,
    daemon=True)
    monitor_thread.start()
    app.run(host='0.0.0.0',port=5000)
