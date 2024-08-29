import openai
import pandas as pd
import os
import json
import tldextract

# Initialize the OpenAI client
# openai.api_key = api_key

def generate_gpt4_response_and_save(endpoint, js_file_path, function_name, output_file_path, model="gpt-4o"):
    try:
        # Read the JavaScript file content
        with open(js_file_path, 'r') as file:
            js_content = file.read()

        # Combine the prompt with the JavaScript content
        combined_prompt = (
            f"Edit this function so that it can't send requests to this endpoint.\n\n"
            f"Here is the JavaScript file content:\n\n"
            f"{js_content}\n\n"
            f"Please edit the function with the name \"{function_name}\" so that it can't send requests to the specified endpoints \"{endpoint}\". "
            f"Return the complete JavaScript code with the modified function."
        )

        # Send a request to the OpenAI API to generate a chat completion
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_prompt}
            ],
            max_tokens=4096,  # Increase max_tokens to allow for larger responses
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Extract the modified JavaScript content, assuming it's within ```javascript``` tags
        modified_js_content = response.choices[0].message['content'].strip()
        
        # Find and extract the content between ```javascript``` tags
        start_tag = "```javascript"
        end_tag = "```"
        start_index = modified_js_content.find(start_tag)
        end_index = modified_js_content.rfind(end_tag)
        if start_index != -1 and end_index != -1 and start_index != end_index:
            code_to_save = modified_js_content[start_index + len(start_tag):end_index].strip()
            # Save the extracted JavaScript content to a new file
            with open(output_file_path, 'w') as output_file:
                output_file.write(code_to_save)
            return 1
        return 0
    except Exception as e:
        # print (f"An error occurred: {e}")
        return 0

def request_response_dic(filename):
    dataset = pd.read_json(filename, lines=True)
    request_response_dic = {}
    for i in dataset.index:
        if dataset["http_req"][i] not in request_response_dic:
            request_response_dic[dataset["http_req"][i]] = dataset["request_id"][i]
    return request_response_dic

def getInitiator(stack):
    if len(stack["callFrames"]) != 0:
        return (
            stack["callFrames"][0]["url"]
            ,
            stack["callFrames"][0]["functionName"]
            # + "@"
            # + str(stack["callFrames"][0]["lineNumber"])
            # + "@"
            # + str(stack["callFrames"][0]["columnNumber"])
        )
    else:
        return getInitiator(stack["parent"])

def get_tracking_functions(filename, request_response_dic):
    # script_url@method: [id, url, method_name, [tracking_reqs]]
    tracking_script_methods = {}
    # reading big request data line by line
    with open(filename) as file:
        for line in file:
            data = json.loads(line)
            for dataset in data:
               if (dataset["call_stack"]["type"] == "script"):
                if (dataset["easylistflag"] == 1
                    or dataset["easyprivacylistflag"] == 1
                    or dataset["ancestorflag"] == 1):
                    script, method = getInitiator(dataset["call_stack"]["stack"])
                    try:
                        script_id = request_response_dic[script]
                        if script +"@" + method not in tracking_script_methods:
                            tracking_script_methods[script + "@" + method] = [script_id, script, method, []]
                        if dataset["http_req"] not in tracking_script_methods[script + "@" + method][3]:
                            tracking_script_methods[script + "@" + method][3].append(dataset["http_req"])
                    except:
                        pass
    return tracking_script_methods

def getDomain(url):
    ext = tldextract.extract(url)
    return ext.domain + "." + ext.suffix                 

def main():
   fold = os.listdir("server/output")
   folder = "server/output/" 

   for f in fold:
        print("generating-surrogates:", f)
        # {request_url: request_id}
        request_id = request_response_dic(folder + f + "/request.json")
        json.dump(request_id, open(folder + f + "/request_id.json", "w"))
        # script_url@method: [id, url, method_name, [tracking_reqs]]
        tracking_functions = get_tracking_functions(folder + f + "/label_request.json", request_id)
        # successfully modified functions:
        success_tracking_functions = {}
        # Write the dictionary to a JSON file
        with open(folder + f + "/tracking_functions.json", 'w') as json_file:
            json.dump(tracking_functions, json_file, indent=4)
        for func in tracking_functions:
            if os.path.exists(folder + f + "/response/" + tracking_functions[func][0] + ".txt"):
                endpoints  = []
                for endpoint in tracking_functions[func][3]:
                    if getDomain(endpoint) not in endpoints:
                        endpoints.append(getDomain(endpoint))
                if os.path.exists(folder + f + "/surrogate/" + tracking_functions[func][0] + "_modified.txt"):
                    val = generate_gpt4_response_and_save(endpoints, folder + f + "/surrogate/" + tracking_functions[func][0] + "_modified.txt", tracking_functions[func][2], folder + f + "/surrogate/" + tracking_functions[func][0] + "_modified.txt")
                else:
                    val = generate_gpt4_response_and_save(endpoints, folder + f + "/response/" + tracking_functions[func][0] + ".txt", tracking_functions[func][2], folder + f + "/surrogate/" + tracking_functions[func][0] + "_modified.txt")
                if val == 1:
                    success_tracking_functions[func] = tracking_functions[func]
        # save the successfully modified functions
        with open(folder + f + "/success_tracking_functions.json", 'w') as json_file:
            json.dump(success_tracking_functions, json_file, indent=4)
main()