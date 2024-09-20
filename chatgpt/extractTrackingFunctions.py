import pandas as pd
import os
import json
import tldextract
import time

def request_response_dic(filename):
    dataset = pd.read_json(filename, lines=True)
    request_response_dic = {}
    for i in dataset.index:
        if dataset["http_req"][i] not in request_response_dic:
            request_response_dic[dataset["http_req"][i]] = dataset["request_id"][i]
    return request_response_dic

# these two functions and implementation is borrowed from label.py ancestor labelling
def CheckAncestoralNodes(callstack):
    # Handling non-script type
    if callstack["type"] != "script":
        return None

    # Initialize a set to track unique script URLs
    unique_scripts = set()
    
    # Recursively insert unique scripts in the stack
    rec_stack_checker(callstack["stack"], unique_scripts)

    # Convert the set to a list and return it
    return list(unique_scripts)

def rec_stack_checker(stack, unique_scripts):
    # Append unique script URLs to the set
    for item in stack["callFrames"]:
        script_url = (
            item["url"]
            + "@"
            + item["functionName"]
            + "@"
            + str(item["lineNumber"])
            + "@"
            + str(item["columnNumber"])
        )
        unique_scripts.add(script_url)

    # Check if the parent object exists and send a recursive call
    if "parent" in stack:
        rec_stack_checker(stack["parent"], unique_scripts)

def get_tracking_functions(filename, request_response_dic):
    # script_url@method@line@column: [id, url, method_name, line, column, [tracking_reqs], [functional_req]]
    script_methods = {}
    # reading big request data line by line
    with open(filename) as file:
        for line in file:
            data = json.loads(line)
            for dataset in data:
               if (dataset["call_stack"]["type"] == "script"):
                unique_scripts = CheckAncestoralNodes(dataset["call_stack"])
                for itm in unique_scripts:
                    if itm not in script_methods.keys():
                        try:
                            script = itm.split('@')[0]
                            mthd = itm.split('@')[1]
                            line = itm.split('@')[2]
                            col = itm.split('@')[3]
                            script_id = request_response_dic[script]
                            script_methods[itm] = [script_id, script, mthd, line, col, [], []]
                        except:
                            pass
                    try:
                        if (dataset["easylistflag"] == 1
                            or dataset["easyprivacylistflag"] == 1
                            or dataset["ancestorflag"] == 1):
                                script_methods[itm][5].append(dataset["http_req"])
                        else:
                                script_methods[itm][6].append(dataset["http_req"])
                    except:
                        pass
        return script_methods

def main():
   fold = os.listdir("server/output")
   folder = "server/output/" 
   for f in fold:
        print("generating-features:", f)
        # {request_url: request_id}
        request_id = request_response_dic(folder + f + "/request.json")
        json.dump(request_id, open(folder + f + "/request_id.json", "w"))
        # script_url@method@line@column: [id, url, method_name, line, column, [tracking_reqs], [functional_req]]
        script_methods = get_tracking_functions(folder + f + "/label_request.json", request_id)
        json.dump(script_methods, open(folder + f + "/features.json", "w"))

main()