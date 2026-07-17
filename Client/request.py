import sys
import requests as rq
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from flask import (Flask,render_template)


balancer_url="http://127.0.0.1:8080"
number=1
#allo command line modification of the number of requests
if(len(sys.argv)>1):
    try:
        number=int(sys.argv[1])
    except(ValueError):
        print("provide integer for count")
        sys.exit(1);

names = []
requests = []
statuses = []


# makes a request to the url of the load_balancer
def make_request(url=urljoin(balancer_url,"home")):
    try:
        res=rq.request('GET',url=url)
        print(res)
        if(res.status_code==200):
            print("request successful")
            return (res.json()),True
        else:
            return (f"request terminated with code {res.status_code} "),False
    except rq.ConnectionError:
        return "could not make connection to the server",False
    
#simulates making the requests over multiple threads
def simulate_requests(no):
    data=[]
    with ThreadPoolExecutor(max_workers=no) as executor:
        results = [executor.submit(make_request) for i in range(0,no)]
    for result in as_completed(results):
        data.append(result.result())
    if(len(data)>=no):
        print("freaking work with me")
        response=make_request(urljoin(balancer_url,"/statistics"))
        data,message=response
        print(data["data"])
        for name, info in data["data"].items():
            names.append(name)
            requests.append(info["requests"])
            statuses.append(info["status"])
    

app=Flask(__name__)
@app.route("/dashboard")
def dashboard():
    res = rq.get("http://127.0.0.1:8080/statistics").json()

    return render_template(
        "dashboard.html",
        stats=res["data"]
    )
if __name__=='__main__':
    simulate_requests(number)
    app.run(host='0.0.0.0',port=5000)

    

    


