import openai
import pandas as pd
import os
import json
import tldextract
import time
import re


openai.api_key = api_key

# def search_function_in_content(js_content, function_name):
#     """
#     Searches for the function in the JavaScript content using a regex pattern.
#     """
#     # Ensure js_content is properly escaped to avoid invalid characters
#     js_content = js_content.encode('unicode_escape').decode('utf-8')

#     # Regex to match various JavaScript function declarations
#     function_pattern = re.compile(
#         rf"""
#         (  # Capture group for the entire function definition
#             # Standard function declaration
#             (function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})     |
#             # Function expression
#             ({re.escape(function_name)}\s*=\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Async function declaration
#             (async\s+function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Async function expression
#             ({re.escape(function_name)}\s*=\s*async\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Arrow function
#             ({re.escape(function_name)}\s*=\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}})       |
#             # Arrow function (single parameter)
#             ({re.escape(function_name)}\s*=\s*[^()\s]+\s*=>\s*\{{[^}}]*\}})        |
#             # Async arrow function
#             ({re.escape(function_name)}\s*=\s*async\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}}) |
#             # Async arrow function (single parameter)
#             ({re.escape(function_name)}\s*=\s*async\s*[^()\s]+\s*=>\s*\{{[^}}]*\}})  |
#             # Object method
#             ({re.escape(function_name)}\s*:\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Async object method
#             ({re.escape(function_name)}\s*:\s*async\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Shorthand object method
#             ({re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})               |
#             # Async shorthand object method
#             (async\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})       |
#             # Class method
#             (\bclass\b[^\{{]+\{{[^}}]*{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}}) |
#             # Async class method
#             (\bclass\b[^\{{]+\{{[^}}]*async\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})
#         )
#         """,
#         re.VERBOSE | re.DOTALL
#     )

#     # Search for the function in the JavaScript file
#     return function_pattern.search(js_content)


# def generate_gpt4_response_and_save(endpoints, js_file_path, function_name, output_file_path, model="gpt-4o"):
#     try:
#         # Read the JavaScript file content
#         with open(js_file_path, 'r') as file:
#             js_content = file.read()

#         # First attempt to find the function using the provided name
#         match = search_function_in_content(js_content, function_name)

#         # If no match, split by '.' and use the last part for searching
#         if not match and '.' in function_name:
#             last_part = function_name.split('.')[-1]
#             print(f"Trying with the last part of the function name: '{last_part}'")
#             match = search_function_in_content(js_content, last_part)

#         if not match:
#             print(f"Function '{function_name}' (or '{last_part}') not found in the JavaScript file.")
#             return 0

#         matched_function = match.group(0)
#         combined_prompt = (
#             f"Given the following JavaScript function:\n\n"
#             f"```javascript\n{matched_function}\n```\n\n"
#             f"And the following inputs:\n"
#             f"1. Function Name: \"{function_name}\"\n"
#             f"2. Endpoints List: {endpoints}\n\n"
#             f"Please modify the function so that it cannot send requests to the provided endpoints. "
#             f"JUST return the modified function in this JSON format enclosed in ```json and ending with ```:\n"
#             f"```json\n{{\"modified-function\": \"\"}}\n```"
#         )

#         response = openai.ChatCompletion.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": combined_prompt}
#             ],
#             n=1,
#             stop=None,
#             temperature=0.7,
#         )

#         response_content = response.choices[0].message['content'].strip()

#         # Parsing the JSON output
#         try:
#             json_start = response_content.find('```json')
#             json_end = response_content.rfind('```')
#             json_str = response_content[json_start + len('```json'):json_end].strip()

#             response_dict = json.loads(json_str)
#             modified_function = response_dict.get("modified-function")

#             if modified_function:
#                 updated_js_content = js_content.replace(matched_function, modified_function)

#                 with open(output_file_path, 'w') as output_file:
#                     output_file.write(updated_js_content)
#                 return 1
#             else:
#                 print("Modified function not found in the GPT-4 response.")
#                 return 0

#         except json.JSONDecodeError as e:
#             print(f"An error occurred while parsing JSON: {e}")
#             return 0

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return 0

# def generate_gpt4_response_and_save(endpoints, js_file_path, function_name, output_file_path, model="gpt-4"):
#     try:
#         print(js_file_path, function_name)
        
#         # Read the JavaScript file content
#         with open(js_file_path, 'r') as file:
#             js_content = file.read()

#         def search_function_in_content(js_content, function_name):
#             """
#             Searches for the function in the JavaScript content using a regex pattern.
#             """
#             # Regex to match various JavaScript function declarations
#             function_pattern = re.compile(
#                 rf"""
#                 (  # Capture group for the entire function definition
#                     # Standard function declaration: function name(...) { ... }
#                     (function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})     |

#                     # Function expression: var name = function(...) { ... }
#                     ({re.escape(function_name)}\s*=\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Async function declaration: async function name(...) { ... }
#                     (async\s+function\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Async function expression: var name = async function(...) { ... }
#                     ({re.escape(function_name)}\s*=\s*async\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Arrow function: var name = (...) => { ... }
#                     ({re.escape(function_name)}\s*=\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}})       |

#                     # Arrow function (with single parameter): var name = param => { ... }
#                     ({re.escape(function_name)}\s*=\s*[^()\s]+\s*=>\s*\{{[^}}]*\}})        |

#                     # Async arrow function: var name = async (...) => { ... }
#                     ({re.escape(function_name)}\s*=\s*async\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}}) |

#                     # Async arrow function (with single parameter): var name = async param => { ... }
#                     ({re.escape(function_name)}\s*=\s*async\s*[^()\s]+\s*=>\s*\{{[^}}]*\}})  |

#                     # Object method: name: function(...) { ... }
#                     ({re.escape(function_name)}\s*:\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Async object method: name: async function(...) { ... }
#                     ({re.escape(function_name)}\s*:\s*async\s*function\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Object arrow method: name: (...) => { ... }
#                     ({re.escape(function_name)}\s*:\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}})       |

#                     # Object async arrow method: name: async (...) => { ... }
#                     ({re.escape(function_name)}\s*:\s*async\s*\([^)]*\)\s*=>\s*\{{[^}}]*\}}) |

#                     # Shorthand object method: name(...) { ... }
#                     ({re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})               |

#                     # Async shorthand object method: async name(...) { ... }
#                     (async\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})       |

#                     # Class method: inside a class, name(...) { ... }
#                     (\bclass\b[^\{{]+\{{[^}}]*{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}}) |

#                     # Async class method: inside a class, async name(...) { ... }
#                     (\bclass\b[^\{{]+\{{[^}}]*async\s+{re.escape(function_name)}\s*\([^)]*\)\s*\{{[^}}]*\}})
#                 )
#                 """,
#             re.VERBOSE | re.DOTALL
#             )

#             # Search for the function in the JavaScript file
#             return function_pattern.search(js_content)

#         # First attempt to find the function using the provided name
#         match = search_function_in_content(js_content, function_name)

#         # If no match, split by '.' and use the last part for searching
#         if not match and '.' in function_name:
#             # Split by '.' and take the last part
#             last_part = function_name.split('.')[-1]
#             print(f"Trying with the last part of the function name: '{last_part}'")
#             match = search_function_in_content(js_content, last_part)

#         if not match:
#             print(f"Function '{function_name}' (or '{last_part}') not found in the JavaScript file.")
#             return 0

#         # Extract the matched function
#         matched_function = match.group(0)
        
#         # Prepare the prompt with the matched function
#         combined_prompt = (
#             f"Given the following JavaScript function:\n\n"
#             f"```javascript\n{matched_function}\n```\n\n"
#             f"And the following inputs:\n"
#             f"1. Function Name: \"{function_name}\"\n"
#             f"2. Endpoints List: {endpoints}\n\n"
#             f"Please modify the function so that it cannot send requests to the provided endpoints. "
#             f"JUST return the modified function in this JSON format enclosed in ```json and ending with ```:\n"
#             f"```json\n{{\"modified-function\": \"\"}}\n```"
#         )

#         # Send a request to the OpenAI API to generate a chat completion
#         response = openai.ChatCompletion.create(
#             model=model,
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": combined_prompt}
#             ],
#             n=1,
#             stop=None,
#             temperature=0.7,
#         )

#         # Extract the JSON-like response content
#         response_content = response.choices[0].message['content'].strip()

#         # Parsing the JSON output
#         try:
#             # Extract JSON part from response (handling possible formatting)
#             json_start = response_content.find('```json')
#             json_end = response_content.rfind('```')
#             json_str = response_content[json_start + len('```json'):json_end].strip()

#             # Convert the response string to a dictionary
#             response_dict = json.loads(json_str)

#             modified_function = response_dict.get("modified-function")

#             if modified_function is not None:
#                 # Replace the original function with the modified one
#                 updated_js_content = js_content.replace(matched_function, modified_function)

#                 # Save the modified JavaScript content
#                 with open(output_file_path, 'w') as output_file:
#                     output_file.write(updated_js_content)
#                 return 1
#             else:
#                 print("Modified function not found in the GPT-4 response.")
#                 return 0

#         except Exception as e:
#             print(f"An error occurred while parsing the response: {e}")
#             return 0

#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return 0

def get_tracking_functions(filename):
    # script_url@method: [id, url, method_name, [tracking_reqs]]
    tracking_script_methods = {}
    with open(filename, 'r') as file:
        data = json.load(file)

    for itm in data:
        if len(data[itm][6]) == 0: 
            if data[itm][1]+"@"+data[itm][2] not in tracking_script_methods:
                tracking_script_methods[data[itm][1]+"@"+data[itm][2]] = [data[itm][0], data[itm][1], data[itm][2], []]
            for req in data[itm][5]:
                tracking_script_methods[data[itm][1]+"@"+data[itm][2]][3].append(req)
    return tracking_script_methods

def contains_only_numbers(input_string):
    # Remove leading and trailing whitespaces
    input_string = input_string.strip()

    # Check if the string contains only digits after removing a possible decimal point
    return input_string.replace(".", "", 1).isdigit()

def getDomain(url):
    ext = tldextract.extract(url)
    return ext.domain + "." + ext.suffix                 

def main():
   fold = os.listdir("server/output")
   folder = "server/output/" 

   for f in fold:
        try:
            print("generating-surrogates:", f)
            # script_url@method: [id, url, method_name, [tracking_reqs]]
            tracking_functions = get_tracking_functions(folder + f + "/features.json")
            json.dump(tracking_functions, open(folder + f + "/tracking_functions.json", "w"))
            # successfully modified functions:
            success_tracking_functions = {}
            # logs
            logs = {
                "script_not_in_request_file": 0,
                "inline_script": 0,
                "replace_function_call_fail": 0,
                "success": 0,
            }
            for func in tracking_functions:
                if contains_only_numbers(tracking_functions[func][0]):
                    if tracking_functions[func][2] != "":
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
                                logs["success"] += 1
                            else:
                                logs["replace_function_call_fail"] += 1
                        else:
                            logs["script_not_in_request_file"] += 1
                    else:
                        logs["replace_function_call_fail"] += 1
                else:
                    logs["inline_script"] += 1

            # save the successfully modified functions
            json.dump(success_tracking_functions, open(folder + f + "/success_tracking_functions.json", 'w'))
            json.dump(logs, open(folder + f + "/surrogate_logs_chatgpt.json", "w"))
        except Exception as e:
            print("Error in generating-surrogates:", f, e)
main()