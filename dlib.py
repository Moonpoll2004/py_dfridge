from dataclasses import dataclass
import json
from urllib.parse import urljoin
from threading import Thread
import time
from requests import request,Response

@dataclass
class EndPoint():
    Method:str
    url_prefix:str


PRE_MP = {
    "ping":EndPoint("POST","/workspace/device/ping"),
    "data":EndPoint("POST","/workspace/device/data"),
    "trigger":EndPoint("POST","/workspace/device/call"),
    "config":EndPoint("POST","/workspace/device/config"),
    "pong":EndPoint("POST","/workspace/device/pong")
}

def call_endpoint(e:EndPoint,data,dhost="http://localhost:4500") -> Response:
    url = urljoin(dhost,e.url_prefix)
    res = request(e.Method,url,data=data)
    return res

class Serializeable():
    def __init__(self) -> None:
        self.encoder = json.JSONEncoder()

    def get_serializeable():
        return 0
    
    def jsonize(self):
        data = self.get_serializeable()
        return self.encoder.encode(data)

class Performer():
    def __init__(self,df_host="http://127.0.0.1:4500",url_prefix="/workspace/device/",method="POST") -> None:
        self.df_host = df_host
        self.url_prefix = url_prefix
        self.url = urljoin(df_host,url_prefix)
        self.method = method

    def perform(self,data=None) -> Response:
        "sending the request to the http server"
        res = request(self.method,self.url,data=data)
        return res
    
    def pre(self,new_prefix):
        "set the url prefix and update the old url"
        self.url_prefix = new_prefix
        self.url = urljoin(self.df_host,self.url_prefix)
    
    def map_end(self,e:EndPoint):
        "mapping endpoint to the url , url prefix and method"
        self.pre(e.url_prefix)
        self.method = e.Method

class Ping(Serializeable):
    def __init__(self,device,workspace) -> None:
        self.device = device
        self.workspace = workspace
        super().__init__()

    def get_serializeable(self):
        return {
            "workspace":self.workspace,
            "device":self.device
        }

class DataRequest(Serializeable):
    def __init__(self,device,workspace,data,type="data") -> None:
        self.device = device
        self.workspace = workspace
        self.data = data
        self.type = type
        super().__init__()

    def get_serializeable(self):
        if isinstance(self.data,dict):
            return {
                "workspace":self.workspace,
                "device":self.device,
                "data":self.data
            }
        elif isinstance(self.data,Serializeable):
            return {
                "workspace":self.workspace,
                "device":self.device,
                "data":self.data.get_serializeable()
            }
        else:
            raise TypeError("The Type of data must be a dict or Serializeable Type")

class TriggerCall(Serializeable):
    def __init__(self,workspace,device,payload,tid) -> None:
        self.workspace = workspace
        self.device = device
        self.payload = payload
        self.trigger = tid
        super().__init__()

    def get_serializeable(self):
        return {
            "workspace":self.workspace,
            "device":self.device,
            "payload":self.payload,
            "trigger":self.trigger
        }


class ConfigGet(Serializeable):
    def __init__(self,workspace,device,config) -> None:
        self.workspace = workspace
        self.device = device
        self.config = config
        super().__init__()

    def get_serializeable(self):
        return {
            "workspace":self.workspace,
            "device":self.device,
            "config":self.config
        }

# ################ #
#health check Func #
# ################ #
def check_health(p,interval=10):
    "Do the healthe check based on interval and Ping Req"
    while True:
        time.sleep(interval)
        print(p)
    


class HealthCheckAutomator():
    def __init__(self,device,workspace,interval=10) -> None:
        self.pong = Ping(device,workspace)
        self.worker = None
        self.interval = interval
    
    def start(self,is_deamon=True):
        try:

            self.worker = Thread(target=check_health,args=[self.pong])
            self.worker.setDaemon(is_deamon)
            self.worker.start()
        except:
            print("The worker gets interrupted")
    
