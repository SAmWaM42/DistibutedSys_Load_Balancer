import sys
import pandas as pd
import matplotlib.pyplot as plt
sys.path.insert(0, '../')
from Balancer.balancer import ring

SLOT_NO=512
VIRTUAL_PER_CONTAINER=9
CONTAINER_NO=3
def A1():
    nRing=ring()
    for name, positions in nRing.lookUp.items():
        print(name, sorted(positions))
    stats={}
    for i in range(0,10000):
        res=nRing.allocateRequest()
        if res != False:
            if res["name"] in stats.keys():
                stats[res["name"]]+=1
            else:
                stats[res["name"]]=1
    plt.barh(list(stats.keys()), list(stats.values()))
    plt.xlabel("Requests")
    plt.ylabel("Servers")
    plt.title("Load Distribution Across Servers")
    plt.savefig("Figures/A1.png")
def A2():
    avg_stats={}
    for j in range(0,4):
        nRing=ring(server_no=2+j)
        stats={}
        for i in range(0,10000):
            res=nRing.allocateRequest()
            if res != False:
                if res["name"] in stats.keys():
                    stats[res["name"]]+=1
                else:
                    stats[res["name"]]=1
        
        avg_stats[2+j] = sum(stats.values()) / (2+j)
    plt.grid(True)
    print(avg_stats)
    plt.plot(list(avg_stats.keys()),list(avg_stats.values()))
    plt.savefig("Figures/A2.png")
A1()
A2()
        
   
            
      
            
            

