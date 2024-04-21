"""Main fact check logic"""
import json
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from lib.whatsapp import whatsapp
from lib import aws, utils, logger, gpt
from lib.fact_check_graph.start import graph

this_logger = logger.configure_logging('FACT_CHECK_LOGIC')


def construct_initial_state_with_history(chat_history):
    """Construct initial state with chat history"""
    initial_state = {
        "messages": [SystemMessage(
            content="Factcheck last user message(s)")],
        "history": chat_history if chat_history else []
    }
    return initial_state


def get_user_message_from_history(chat_history):
    """Function to get the user message from the chat history"""
    try:
        this_logger.info("Getting user message from chat history")
        message = next((msg for msg in chat_history if isinstance(msg, HumanMessage) and msg.name == 'User'), None)
        this_logger.debug("User message: %s", message.content)
        return message

    except Exception as e:
        this_logger.error("Error getting user message from chat history: %s", e)
        return None


def fact_check_message(number, message_id, media_id, timestamp, language=None):
    """function that process """
    this_logger.info('\nFact check message...')
    # Confirm if new message has arrived
    if aws.confirm_if_new_msg(number, timestamp):
        return utils.create_api_response(400, 'New message has been received')

    # Set initial state
    chat_history = aws.get_chat_history(number)
    initial_state = construct_initial_state_with_history(chat_history)
    user_message = get_user_message_from_history(chat_history)

    # Fact Check
    response = graph.invoke(initial_state)
    final_message_content = response.get("messages")[-1].content
    this_logger.debug('final_message_content: %s', final_message_content)

    # Sumup and save data in DynamoDB Table:
    if aws.save_in_db(final_message_content, number, f'{user_message.id}_r', 'bot'):
        chat_history = [AIMessage(content=final_message_content, name='Fact_Checker')] + chat_history
        this_logger.debug('\nchat_history: %s', chat_history)
        chat_history = utils.langchain_message_to_dict(chat_history)
        sumup = gpt.summarize_with_gpt3_langchain(
            json.dumps(chat_history)).get('summarized_message')
        if sumup is None:
            this_logger.debug('sumup is None')
            return utils.create_api_response(400, 'Failed to create sumup')
        if aws.save_in_db(sumup, number, f'{user_message.id}_s', 'sumup'):
            # Send message to user
            return whatsapp.send_message(number, final_message_content,
                                         'interactive_main_menu', language)
    return utils.create_api_response(400, 'Failed to save messages to db')
