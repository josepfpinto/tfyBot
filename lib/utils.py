"""Useful classes and functions"""
import logging
import json
import re
from flask import jsonify


class RequestType:
    """Function to calculate cost based on number of tokens"""

    def __enum__(self):
        pass

    GPT = 'GPT'
    FREE = 'FREE'
    PERPLEXITY = 'PERPLEXITY'


TRANSLATE_JSON_KEYS = '''{translated_message: <Only the translated message in english>, original_language: <original langugage of the user message>}'''

TRANSLATE = f'''Translate the user message to english and identify the original language. Format of the response should be a json (ready to be converted by json.loads) with these keys: {
    TRANSLATE_JSON_KEYS} '''

JSON_KEYS = '''{truthfulness: <FALSE | PROBABLY FALSE | PROBABLY TRUE | TRUE>, explanation: <Clear, plain language explanation>, links: <List of current, verified evidence links or an empty list if none apply>}'''

ANALYSE_USER_MESSAGE = f'''Analyse the content of the user claim and provide an assessment of its truthfulness in simple and plain language using your own knowledge and websearch, indicating the probability of being true or false and the reasoning behind this assessment, together with verified existing links that support this assessment. If no suitable links are available or the existing ones cannot be verified, provide an empty list of links.
Format of the final response/output should be a json (ready to be converted by json.loads) with these keys: {JSON_KEYS}
A preliminary fact-check was done with this result: '''

REVIEW_ANALYSIS_INSTRUCTION = f'''Please review the provided assessment regarding the truthfulness of a user's claim. Adjust the assessment if necessary, ensuring accuracy and objectivity. Verify the functionality and relevance of the supplied links list, removing any link that is not available or not relevant, providing an empty list.
Format of the response should be a json (ready to be converted by json.loads) with these keys: {JSON_KEYS}
Previous fact-check (in the same JSON format):
'''


def clean_and_convert_to_json(input_str):
    """Function to convert string into json"""
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
        logging.error("Error decoding JSON: %s", e)
        return {}


def json_to_formatted_string(json_data):
    """Function to convert a json with 'truthfulness', 'explanation' and 'links' keys into a formatted string"""
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


def calculate_cost(request_type=RequestType.GPT, tokens=0, cost=0, prompt_tokens=0, completion_tokens=0):
    """Function to calculate cost based on number of tokens"""
    if request_type == RequestType.GPT:
        return {"type": request_type, "tokens": tokens, "price": round(cost, 4)}

    if request_type == RequestType.PERPLEXITY:
        # Pricing details
        price_per_million_input_tokens = 0.07
        price_per_million_output_tokens = 0.28
        # Calculate cost for prompt and completion tokens
        input_cost = (prompt_tokens / 1_000_000) * \
            price_per_million_input_tokens
        output_cost = (completion_tokens / 1_000_000) * \
            price_per_million_output_tokens
        return {"type": request_type, "tokens": tokens, "price": round(input_cost + output_cost, 4)}

    if request_type == RequestType.FREE:
        return {"type": request_type, "tokens": 0, "price": 0}


def get_dynamic_max_tokens(claim):
    """Function to calculate max tokens based on claim length"""
    return 200 + len(claim) // 20


def create_api_response(status, message):
    """Function to create API response - {status: string, message: string}, status: int"""
    statusString = "ok" if status == 200 else "error"
    return jsonify({"status": statusString, "message": message}), status