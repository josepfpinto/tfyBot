import json
import re


def clean_and_convert_to_json(input_str):
    # Attempt to clean the input string
    # Remove any trailing characters that are not part of the JSON object
    cleaned_str = re.sub(r'\}\'.*$', '}', input_str.strip())

    # Directly parse the cleaned input string into a Python dictionary
    try:
        data = json.loads(cleaned_str)

        # Post-process the dictionary to remove keys with empty or 'null' values
        cleaned_data = {k: v for k, v in data.items() if v and v != 'null'}

        return cleaned_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}


def json_to_formatted_string(json_data):
    # Define the keys in order and how to format them
    key_order_and_format = [
        ("truthfulness", "{} \n"),
        ("explanation", "{} \n"),
        ("links", "Links: {}")
    ]

    formatted_parts = []
    for key, format_str in key_order_and_format:
        value = json_data.get(key)
        if value:
            if isinstance(value, list):
                # Join list items with a comma if the value is a list (for links)
                formatted_parts.append(format_str.format(", ".join(value)))
            else:
                # Directly format the string value
                formatted_parts.append(format_str.format(value))

    # Join all parts with new lines and return
    return "\n".join(formatted_parts)
