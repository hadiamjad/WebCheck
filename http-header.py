"""#### Import"""

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

"""#### EasyList & EasyPrivacyList
- update the EasyList and EasyPrivacyList file paths

`CheckTrackingReq(rules, url, top_level_url, resource_type)`
"""


# Description: append the filter rules list
# input: filename = file containing easylist and easyprivacylist
# return: Adblock rules object
def getRules(filename):
    df = pd.read_excel(filename)
    rules = []
    for i in df.index:
        rules.append(df["url"][i])
    Rules = AdblockRules(rules)
    return Rules


# Description: setting predefined rules
easylist = getRules("EasyPrivacyList.xlsx")
easyPrivacylist = getRules("easyList.xlsx")


# Description: extract domain from given url
# input: url = url for which domain is needed
# return: domain
def getDomain(url):
    ext = tldextract.extract(url)
    return ext.domain + "." + ext.suffix


# Description: check if its thirparty request
# input: url = url
# input: top_level_url = top_level_url
# return: returns True if its thirdparty request otherwise false
def isThirdPartyReq(url, top_level_url):
    d_url = getDomain(url)
    d_top_level_url = getDomain(top_level_url)
    if d_url == d_top_level_url:
        return False
    else:
        return True


# Description: check if the request is tracking or non-tracking
# input: rules = Adblock rules object
# input: url = url
# input: top_level_url = top_level_url
# input: resource_type = resource_type
# return: returns True if it has tracking status otherwise false
def CheckTrackingReq(rules, url, top_level_url, resource_type):
    return int(
        rules.should_block(
            url,
            {
                "resource_type": resource_type,
                "domain": getDomain(url),
                "third-party": isThirdPartyReq(url, top_level_url),
            },
        )
    )

# Function to read JSON file line by line
def read_json_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def get_http_header(JSONfile_path):
    # # reading file as dataframe
    request_data_list = read_json_file(JSONfile_path + "/request.json")
    request_info_data_list = read_json_file(JSONfile_path + "/requestInfo.json")
    response_data_list = read_json_file(JSONfile_path+ "/responses.json")

    # Add easylistflag and easyprivacylistflag to each request_data dictionary
    for request_data in request_data_list:
        request_data['easylistflag'] = CheckTrackingReq(
            easylist, request_data['http_req'], request_data['frame_url'], request_data['resource_type']
        )
        request_data['easyprivacylistflag'] = CheckTrackingReq(
            easyPrivacylist, request_data['http_req'], request_data['frame_url'], request_data['resource_type']
        )
    # key: request-id 
    # value: {header: , url:, ....}
    result = {}

    # Iterate through the request data and merge with corresponding requestInfo and response data
    for request_data in request_data_list:
        request_id = request_data['request_id']
    
        # Initialize the entry for this request_id
        result[request_id] = {
            'http_req': request_data.get('http_req'),
            'top_level_url': request_data.get('top_level_url'),
            'frame_url': request_data.get('frame_url'),
            'resource_type': request_data.get('resource_type'),
            'requests_headers': request_data.get('header', {}),
            'easylistflag': request_data.get('easylistflag'),
            'easyprivacylistflag': request_data.get('easyprivacylistflag')
        }
        
        # Find the corresponding requestInfo data
        for request_info_data in request_info_data_list:
            if request_info_data['request_id'] == request_id:
                result[request_id]['requestInfoHeaders'] = request_info_data.get('headers', {})
                result[request_id]['requestInfo_cookies'] = {cookie['cookie']['name']: cookie['cookie'] for cookie in request_info_data.get('cookies', [])}
                break
        
        # Find the corresponding response data
        for response_data in response_data_list:
            if response_data['request_id'] == request_id:
                result[request_id]['response_headers'] = response_data['response'].get('headers', {})
                break

    # Define the output file path
    output_file_path = os.path.join(JSONfile_path, 'http-header.json')

    # Write the result dictionary to the output file
    with open(output_file_path, 'w') as output_file:
        json.dump(result, output_file, indent=4)

    print(f"Result has been written to {output_file_path}")



def main():
    fold = os.listdir("server/output")
    count = 0
    for f in fold:
        try:
            print("labeled: ", f)
            get_http_header(
                "server/output/" + f + "/",
            )
            count += 1
        except:
            print("not-http-header: ", f)


main()