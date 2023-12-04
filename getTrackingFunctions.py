import pandas as pd
import numpy as np
import os
import json
import math
import time
import tldextract
import traceback
from urllib.parse import urlparse
from adblockparser import AdblockRules

def getInitiator(stack):
    if len(stack["callFrames"]) != 0:
        return (
            stack["callFrames"][0]["url"]
            + "@"
            + stack["callFrames"][0]["functionName"]
        )
    else:
        return getInitiator(stack["parent"])

# script sample -> at l (https://c.amazon-adsystem.com/aax2/apstag.js:2:1929)
# return https://c.amazon-adsystem.com/aax2/apstag.js
def getStorageScriptFromStackWebGraph(script):
    try:
        script = script.split("\n")[2]
        method = script.split("(")[0].strip().split(" ")[1]  # l
        script = script.split("(")[
            1
        ]  # https://c.amazon-adsystem.com/aax2/apstag.js:2:1929)
        return (
            "https:" + script.split(":")[1] + "@" + method
        )
    except:
        pass

def get_tracking_functions_request(folder, dic):
    tracking_requests = []
    with open(folder + "/label_request.json") as file:
            for line in file:
                try:
                    data = json.loads(line)
                    for dataset in data:
                        try:
                            # if-script-initiated
                            if dataset["call_stack"]["type"] == "script":
                                # if-tracking-request
                                # then get the top of the call stack that
                                # contains info about function that called 
                                # fetch or XMLHTTPRequest
                                if (
                                    dataset["easylistflag"] == 1
                                    or dataset["easyprivacylistflag"] == 1
                                    or dataset["ancestorflag"] == 1
                                ):
                                    function = getInitiator(dataset["call_stack"]["stack"])
                                    if function not in dic.keys():
                                        dic[function]="network"
                            # saving all tracking requests
                            if (
                                    dataset["easylistflag"] == 1
                                    or dataset["easyprivacylistflag"] == 1
                                    or dataset["ancestorflag"] == 1
                                ):
                                if dataset["http_req"] not in tracking_requests:
                                    tracking_requests.append(dataset["http_req"])
                        except Exception as E:
                            print("Network 1:", E)  
                except Exception as E:
                      print("Network 2:", E)    
    return tracking_requests 

def get_tracking_functions_storage(folder, dic, tracking_requests):
    try:
        with open(folder + "/cookie_storage.json") as file:
            for line in file:
                try:
                    dataset = json.loads(line)
                    function = getStorageScriptFromStackWebGraph(dataset["stack"])
                    script = function.split("@")[0]
                    if script in tracking_requests:
                        if function not in dic.keys():
                            dic[function]="storage"
                except Exception as e:
                    print("Storage 1:", e)
    except Exception as e:
        print("Storage 2:", e)

def main():
    fold = os.listdir("server/output")
    for f in fold:
        print(f)
        tracking_functions = {}
        tracking_requests = get_tracking_functions_request("server/output/" + f, tracking_functions)
        get_tracking_functions_storage("server/output/" + f, tracking_functions, tracking_requests)
        with open("server/output/" + f + '/tracking_functions.json', 'w') as json_file:
            json.dump(tracking_functions, json_file)


main()