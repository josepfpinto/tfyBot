"""Main fact check logic"""
import logging
import requests
from . import gpt
from . import whatsapp, aws, utils


def initial_fact_checking(claim, cost_info):
    """
    Fact-checking by querying an external API.
    """
    api_url = f"https://nli.wmflabs.org/fact_checking_aggregated/?claim={
        requests.utils.quote(claim)}"
    headers = {"accept": "application/json"}

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        if response.status_code == 200:
            cost_info.append(utils.calculate_cost(utils.RequestType.FREE))
            return response.json()
        else:
            return f"Failed to fetch initial fact-checking data {response.status_code}"
    except Exception as e:
        return f"Exception occurred on initial fact-checking: {e}"


def fact_check(previous_user_messages, cost_info):
    """
    Process a fact-check request through initial fact-checking and deep analysis.
    """
    # Parse previous user messages into 'last conversation messages: user(timestamp): <user_message_or_claims>; aibot(timestamp): <aibot_message>; sumup(timestamp): <conversation_sumup>; ...'
    messages = serialize_last_messages(previous_user_messages)

    # Step 1: Initial Fact-Checking with Datasets/APIs
    # TODO: improve focusing on wikipedia AND https://toolbox.google.com/factcheck/apis OR WikipediaAPIWrapper!
    fact_check_result = initial_fact_checking(messages, cost_info)

    # Step 2: Advanced Analysis with LLM (includes fecthinf urls)
    deep_analysis_result = gpt.analyse_claim(
        messages, fact_check_result, cost_info)

    # Step 3: Review analysis
    # TODO: Improve implementation with GPT-4 to confirm answer and provide a nuanced perspective
    # TODO: Include the request to assure the answer has no more than xxx char
    # deep_analysis_result_gpt = gpt.review_previous_analysis(message, json.dumps(deep_analysis_result_perplexity), cost_info)

    # Output results
    return {
        "initial_fact_check_result": fact_check_result,
        "deep_analysis": utils.json_to_formatted_string(deep_analysis_result),
    }


def fact_check_message(previous_user_messages, number, message_id, media_id, timestamp, cost_info, language=None):
    """function that process """
    # Check if new message exists
    if aws.confirm_if_new_msg(number, timestamp):
        return utils.create_api_response(400, 'newer message exists')

    # Fact-Checking
    response = fact_check(previous_user_messages, cost_info)
    logging.info(response)

    # Placeholder Step 9: Sumup and save data in DynamoDB Table:
    aws.save_in_db(response, number, message_id, media_id, timestamp)

    # Send message to user
    return whatsapp.send_message(number, response['deep_analysis'], cost_info, 'interactive_main_menu', language)
