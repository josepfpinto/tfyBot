"""Useful classes and functions"""
import logging
import json
import re
import sys
from flask import jsonify


class RequestType:
    """Function to calculate cost based on number of tokens"""

    def __enum__(self):
        pass

    GPT = 'GPT'
    FREE = 'FREE'
    PERPLEXITY = 'PERPLEXITY'


WHATSAPP_CHAR_LIMMIT = 350
HISTORY_CHAR_LIMMIT = 3500
MAX_TOKENS = 0

SUPERVISOR_PROMPT = '''As a Supervisor of a fact checker bot, your role is to oversee
        a dialogue between these workers: {AGENTS}.
        Based on the user's request and chat history, 
        determine which worker should take the next action. Each worker is responsible for
        executing a specific task and reporting back their findings and progress.
        Once all tasks are complete, indicate with 'FINISH'.'''
SUPERVISOR_QUESTION = '''Given the conversation above, who should act next?
        Or should we FINISH? Select one of: {OPTIONS}'''

CATEGORIZE_USER_MESSAGE_JSON_KEYS = '''{value: <GREETINGS | LANGUAGE | FACTCHECK>}'''
CATEGORIZE_USER_MESSAGE = '''Categorize the last message from a user into three categories: GREETINGS, LANGUAGE or FACTCHECK.
    If the message contains the name of a language, categorize it as LANGUAGE.
    Else, if the message is a simple greeting or doesn't clearly require fact-checking, categorize it as GREETINGS. 
    Otherwise, if it contains information (or partial information) that might require verification, categorize it as FACTCHECK. 
    For context, the previous messages exchanged with the user were also included.
    Format of the response should be a json (ready to be converted by json.loads) 
    with these keys: {CATEGORIZE_USER_MESSAGE_JSON_KEYS}'''

TRANSLATE_JSON_KEYS = '''{translated_message: <translated message | empty string>}'''
TRANSLATE = '''If necessary, translate the user message to {LANGUAGE}. If no translation is necessary send an empty string.
    Format of the response should be a json (ready to be converted by json.loads) with these keys: {TRANSLATE_JSON_KEYS}'''

SUMMARIZE_JSON_KEYS = '''{summarized_message: <summarized message>}'''
SUMMARIZE = '''Summarize the following chat history up to a max of {CHAR_LIMIT} chars.
    Format of the response should be a json (ready to be converted by json.loads) with these keys: {SUMMARIZE_JSON_KEYS}'''

ANALYSE_USER_MESSAGE = ''' You are a Fact Checker Agent. Your task involves analyzing user claims in a chat conversation step by step.
        Based on this chat conversation with an user and other ai agents, analyse the content of the user claim(s) and provide an assessment of its truthfulness.
        1. Identify up to 3 topics from the user's message. 
        2. Conduct internet searches on each topic, one at a time.
        3. Assess the truthfulness of the claims, categorizing them as FALSE, PROBABLY FALSE, PROBABLY TRUE, or TRUE. And provide
        a straightforward explanation for your assessment, supported by up to 3 credible sources. If reliable sources are not available, state so.
        Ensure your final response is concise and based on factual evidence.
        '''
REVIEW_ANALYSIS_INSTRUCTION = '''You are a Reviewer Agent tasked with evaluating the Fact Checker Agent's analysis of user claims.
        Based on this chat conversation with an user and other ai agents, please review the provided assessment from Fact Checker Agent
        regarding the truthfulness of the user claim(s).
        1. Cross-check the accuracy and objectivity of the assessment using a different source.
        2. If you find discrepancies or inaccuracies, explain why the original assessment might be incorrect, providing a new source for reference.
        3. If the assessment holds true, validate its correctness with an explanation and a supporting source.
        Your review should ensure the assessment is both accurate and impartial.
        '''

EDITOR_INSTRUCTION = f''' You are an Editor Agent, responsible for finalizing the assessments made by both the Fact Checker Agent and the Reviewer Agent regarding user claims.
        1. Evaluate the quality and bias of the assessments. If you identify any issues, explain the shortcomings.
        2. Confirm the validity and relevance of all cited sources, removing any that are unsuitable.
        3. Craft a WhatsApp message to the user with a friendly greeting, a concise verdict (False, Probably False, Probably True, True),
        a summary of findings, and links to up to 3 verified sources. Keep your message under {WHATSAPP_CHAR_LIMMIT} characters.
        Your role is to ensure the final message is clear, unbiased, and user-friendly.
        '''


DEFAULT_SYSTEM_PROMPT = '''{INSTRUCTION} Format of the response should be a json (ready to be converted by json.loads)
    with these keys: {JSON_KEYS} Previous fact-check: {FACT_CHECK}'''
DEFAULT_USER_PROMPT = '''Last messages and user claim (format: 'last conversation messages:
    user(timestamp): <user_message_or_claims>; aibot(timestamp): <aibot_message>; sumup(timestamp): <conversation_sumup>; ...'): {MESSAGE}'''


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


def create_api_response(status, message):
    """Function to create API response - {status: string, message: string}, status: int"""
    statusString = "ok" if status == 200 else "error"
    return jsonify({"status": statusString, "message": message}), status


def get_dynamic_max_tokens(max_tokens, messages):
    """Function to calculate max tokens based on messages length"""

    if max_tokens == 0:
        return 200 + len(messages) // 10
    return max_tokens


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
