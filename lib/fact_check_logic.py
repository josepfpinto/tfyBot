"""Main fact check logic"""
import json
from langchain_core.messages import SystemMessage, AIMessage
from whatsapp import whatsapp
from . import gpt
from . import aws, utils, logger
from .fact_check_graph.start import graph

this_logger = logger.configure_logging('FACT_CHECK_LOGIC')


# def initial_fact_checking(claim):
#     """
#     Fact-checking by querying an external API.
#     """
#     api_url = f"https://nli.wmflabs.org/fact_checking_aggregated/?claim={
#         requests.utils.quote(claim)}"
#     headers = {"accept": "application/json"}

#     try:
#         response = requests.get(api_url, headers=headers, timeout=20)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             return f"Failed to fetch initial fact-checking data {response.status_code}"
#     except Exception as e:
#         return f"Exception occurred on initial fact-checking: {e}"


# def fact_check(previous_user_messages):
#     """
#     Process a fact-check request through initial fact-checking and deep analysis.
#     """

#     # Step 1: Initial Fact-Checking with Datasets/APIs
#     # TODO: improve focusing on wikipedia AND https://toolbox.google.com/factcheck/apis OR WikipediaAPIWrapper!
#     fact_check_result = initial_fact_checking(previous_user_messages)

#     # Step 2: Advanced Analysis with LLM (includes fecthinf urls)
#     deep_analysis_result = gpt.analyse_claim(
#         previous_user_messages, fact_check_result)

#     # Output results
#     return {
#         "initial_fact_check_result": fact_check_result,
#         "deep_analysis": utils.json_to_formatted_string(deep_analysis_result),
#     }


def construct_initial_state_with_history(chat_history):
    initial_state = {
        "messages": [SystemMessage(
            content="Factcheck last user message(s)")],
        "history": chat_history if chat_history else []
    }
    return initial_state


def fact_check_message(number, message_id, media_id, timestamp, language=None):
    """function that process """
    # Confirm if new message has arrived
    if aws.confirm_if_new_msg(number, timestamp):
        return utils.create_api_response(400, 'New message has been received')

    # Set initial state
    chat_history = aws.get_chat_history(number)
    initial_state = construct_initial_state_with_history(chat_history)

    # Fact Check
    response = graph.invoke(initial_state)
    final_message_content = response.get("messages")[0].content
    this_logger.info('response: %s', response)
    this_logger.info('final_message_content: %s', final_message_content)

    # Sumup and save data in DynamoDB Table:
    if aws.save_in_db(final_message_content, number, f'{message_id}_r', 'bot'):
        chat_history.append(
            AIMessage(content=final_message_content, name='Fact_Checker'))
        sumup = gpt.summarize_with_gpt3_langchain(
            json.dumps(chat_history)).get('summarized_message')
        if sumup is None:
            return utils.create_api_response(400, 'Failed to create sumup')
        if aws.save_in_db(sumup, number, f'{message_id}_s', 'sumup'):
            # Send message to user
            return whatsapp.send_message(number, final_message_content,
                                         'interactive_main_menu', language)
    return utils.create_api_response(400, 'Failed to save messages to db')
