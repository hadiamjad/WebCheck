import ast
import os
import json
from pathlib import Path

def main():

    with open('/home/grads/hadiamjad/repositories/llm-code-refactor/server/output_surr/booking.com/pageErrors.txt', 'r') as file:
        data = file.read()

    # Step 2: Parse the data
    parsed_data = ast.literal_eval(data)

    # Step 3: Count the occurrences of 'severe'
    severe_count = sum(1 for item in parsed_data if (item.get('level') == 'SEVERE' and 'localhost' not in item.get('message') and 'chrome-extension' not in item.get('message')))

    # Output the result
    print(f"The count of 'severe' levels is: {severe_count}")

main()