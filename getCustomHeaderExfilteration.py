import requests
from bs4 import BeautifulSoup
import json
import os
import tldextract
import pandas as pd
from urllib.parse import urlparse
import traceback
from urllib.parse import urlparse
from adblockparser import AdblockRules


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


def fetch_default_headers():
    url = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        headers_mdn = soup.select("div.section-content dl dt a code")
        headers_mdn = [header.get_text() for header in headers_mdn]
        headers_mdn.append("p3p")
        headers_mdn = list(map(str.lower, headers_mdn))
        return headers_mdn
    else:
        print(f"Failed to fetch headers from MDN. Status code: {response.status_code}")
        return []

def fetch_rfc4229_headers():
    URL = "https://www.rfc-editor.org/rfc/rfc4229.html"
    headers = []
    
    try:
        response = requests.get(URL, timeout=60)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Page 5 headers
        page5 = soup.find(attrs={"id": "page-5"}).parent
        header_text = list(page5.children)[5]
        headers.extend(header_text.split()[5::2])
        
        # Page 6 headers
        page6 = soup.find(attrs={"id": "page-6"}).parent
        header_text = list(page6.children)[3]
        headers.extend(header_text.split()[::2])
        
        # Page 7 headers
        page7 = soup.find(attrs={"id": "page-7"}).parent
        header_text = list(page7.children)[3]
        headers.extend(header_text.split()[::2])
        
        return headers
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching RFC content: {e}")
        return []

default_headers = fetch_default_headers()    
rfc4229_headers = fetch_rfc4229_headers()
default_headers = list(set(default_headers + rfc4229_headers))
default_headers.extend([":authority", ":method", ":path", ":scheme"])

# Function to read JSON file line by line
def read_json_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            data.append(json.loads(line))
    return data

def check_custom_header_in_req(custom_header, req):
    ret = []
    for header in custom_header:
        for val in custom_header[header]:

            if val in req and len(val) > 5:
                if ["req", header, val, req] not in ret:
                    ret += ["req", header, val, req]
    return ret

def check_custom_header_in_req_cookie(custom_header, cookie_val):
    ret = []
    for header in custom_header:
        for val in custom_header[header]:
            if val in cookie_val and len(val) > 5:
                if ["req_cookie", header, val, cookie_val] not in ret:
                    ret += ["req_cookie", header, val, cookie_val]
    return ret

def check_custom_header_in_cookie(custom_header, cookie):
    ret = []
    for header in custom_header:
        for val in custom_header[header]:
            if val in cookie and len(val) > 5:
                if ["cookie", header, val, cookie] not in ret:
                    ret += ["cookie", header, val, cookie]
    return ret

def get_http_header(JSONfile_path):

    with open(JSONfile_path + "http-header.json", 'r') as file:
        http_header_list = json.load(file)
    custom_header = {}

    for request_id, details in http_header_list.items(): 
        request_headers = details.get('requests_headers', {})
        for header in request_headers:
            if header.lower() not in default_headers:
                if header.lower() not in custom_header:
                    custom_header[header.lower()] = []
                if request_headers[header] not in custom_header[header.lower()]:
                    custom_header[header.lower()].append(request_headers[header])
        
        requestInfo_headers = details.get('requestInfoHeaders', {})
        for header in requestInfo_headers:
            if header.lower() not in default_headers:
                if header.lower() not in custom_header:
                    custom_header[header.lower()] = []
                if requestInfo_headers[header] not in custom_header[header.lower()]:
                    custom_header[header.lower()].append(requestInfo_headers[header])
        
        response_headers = details.get('response_headers', {})
        for header in response_headers:
            if header.lower() not in default_headers:
                if header.lower() not in custom_header:
                    custom_header[header.lower()] = []
                if response_headers[header] not in custom_header[header.lower()]:
                    custom_header[header.lower()].append(response_headers[header])

    ret_matches = []
    tracking_req_ids = []
    # request_data_list = read_json_file(JSONfile_path + "/label_request.json")
    with open(JSONfile_path + "label_request.json") as file:
        for line in file:
            request_data_list = json.loads(line)
            for request_data in request_data_list:
                if request_data['easylistflag'] == 1 or request_data['easyprivacylistflag'] == 1:
                    ret_matches += check_custom_header_in_req(custom_header, request_data['http_req'])
                    tracking_req_ids.append(request_data['request_id'])
    
    if os.path.exists(JSONfile_path + "requestInfo.json"):
        request_info_data_list = read_json_file(JSONfile_path + "requestInfo.json")
        for request_info_data in request_info_data_list:
            if request_info_data['request_id'] in tracking_req_ids:
                try:
                    if len(request_info_data['cookies']) > 0:
                        for item in request_info_data['cookies']:
                            for key in item['cookie'].keys():
                                ret_matches += check_custom_header_in_req_cookie(custom_header, item['cookie'][key])
                except:
                    pass
    
    if os.path.exists(JSONfile_path + "cookie_storage.json"):
        cookie_data_list = read_json_file(JSONfile_path + "cookie_storage.json")
        for cookie_data in cookie_data_list:
            if 'cookie' in cookie_data:
                ret_matches += check_custom_header_in_cookie(custom_header, cookie_data['cookie'])
    
    return ret_matches

def main():
    fold = os.listdir("server/output")
    count = 0
    ret = []
    for f in fold:
        try:
            print("labeled: ", f)
            ret = get_http_header(
                "server/output/" + f + "/",
            )
            with open("server/output/" + f + "/"+ "exfilteration.json", 'w') as file:
                json.dump(ret, file)
            count += 1
            # break
        except Exception as e:
            print("not-http-header: ", f, e)


main()
