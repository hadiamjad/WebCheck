import os
import json
import numpy as np

# Function to remove outliers using the IQR method
def remove_outliers(data):
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return [x for x in data if lower_bound <= x <= upper_bound]

# Initialize dictionaries to store all values for each metric
values_output = {"dom_content_loaded": [], "dom_interactive": [], "load_event_time": [], "total_heap_size": [], "used_heap_size": []}
values_output_surr = {"dom_content_loaded": [], "dom_interactive": [], "load_event_time": [], "total_heap_size": [], "used_heap_size": []}

# Get the list of folders
folders = os.listdir("server/output")

for folder in folders:
    # Check and read performance.json in output
    output_path = os.path.join("server/output", folder, "performance.json")
    # Check and read performance.json in output_surr
    output_surr_path = os.path.join("server/output_surr", folder, "performance.json")
    if os.path.isfile(output_path) and os.path.isfile(output_surr_path):
        with open(output_path) as file:
            data = json.load(file)
            for key in values_output:
                if key in data:
                    values_output[key].append(data[key])
        with open(output_surr_path) as file:
            data = json.load(file)
            for key in values_output_surr:
                if key in data:
                    values_output_surr[key].append(data[key])

# Compute and print the averages for output after removing outliers
print("Averages for output (Outliers Removed):")
for key in values_output:
    filtered_values = remove_outliers(values_output[key])
    if filtered_values:
        average = sum(filtered_values) / len(filtered_values)
        print(f"{key}: {average}")
    else:
        print(f"{key}: No data or all data are outliers")

# Compute and print the averages for output_surr after removing outliers
print("Averages for output_surr (Outliers Removed):")
for key in values_output_surr:
    filtered_values = remove_outliers(values_output_surr[key])
    if filtered_values:
        average = sum(filtered_values) / len(filtered_values)
        print(f"{key}: {average}")
    else:
        print(f"{key}: No data or all data are outliers")
