import os
import json
from pathlib import Path

# helper functions for breakpoints
def getInitiator(stack):
    try:
        if len(stack["callFrames"]) != 0:
            if (
                "chrome-extension" not in stack["callFrames"][0]["url"]
                and stack["callFrames"][0]["url"] != ""
            ):
                return {
                    "url": stack["callFrames"][0]["url"],
                    "functionName": stack["callFrames"][0]["functionName"],
                }
        else:
            return getInitiator(stack["parent"])
    except:
        pass


def read_json(file_path):
    """Reads a JSON file and returns the data."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading {file_path}: {e}")
        return {}

def count_total_requests(data):
    """Counts the total requests from the given JSON data."""
    total = 0
    for key in data.keys():
        total += len(data[key][3])
    return total

def process_label_request_file(file_path, success_data):
    """Processes each line in the label_request.json file and counts not blocked requests."""
    not_blocked = 0
    try:
        with open(file_path) as file:
            for line in file:
                data = json.loads(line)
                for dataset in data:
                    if dataset["call_stack"]["type"] == "script":
                        try:
                            val = getInitiator(dataset["call_stack"]["stack"])
                            key = f"{val['url']}@{val['functionName']}"
                            if key in success_data and dataset["http_req"] in success_data[key][3]:
                                not_blocked += 1
                                print(key)
                        except:
                            pass
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error processing {file_path}: {e}")
    return not_blocked

def main():
    output_dir = Path("server/output")
    output_surr_dir = Path("server/output_surr")
    not_blocked = 0
    total = 0

    for folder in output_dir.iterdir():
        surrogate_path = output_surr_dir / folder.name / "surrogate"
        if surrogate_path.exists() and surrogate_path.is_dir() and len(list(surrogate_path.iterdir())) > 0:
            print(folder.name)
            # Read the JSON file for tracking functions
            success_data = read_json(output_surr_dir / folder.name / "success_tracking_functions.json")
            # Count total requests
            total += count_total_requests(success_data)
            print(count_total_requests(success_data))
            # Process label requests
            label_request_path = output_dir / folder.name / "label_request.json"
            not_blocked += process_label_request_file(label_request_path, success_data)
            print(process_label_request_file(label_request_path, success_data))

    print(f"Total requests: {total}, Not blocked: {not_blocked}")

if __name__ == "__main__":
    main()