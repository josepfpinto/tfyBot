"""Testing"""
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from lib import utils, logger
from lib.whatsapp.whatsapp import send_template_message, send_message
from lib.fact_check_graph.start import graph

logger = logger.configure_logging('TEST')
load_dotenv()
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
number = '351xxxxxxxxx'

initial_state = {
    "messages": [HumanMessage(content=DUMMY_MESSAGE)],
    "history": []
}
response = graph.invoke(initial_state)
final_message_content = response.get("messages")[0].content
logger.info('response: %s', response)
logger.info('final_message_content: %s', final_message_content)

# -------------
# Resolver /test

# Test AWS...

# Test environment variables
# utils.create_api_response(200, f'Testing - TOKEN: {TOKEN}')

# Test saving user in db
# if aws.save_in_db(DUMMY_MESSAGE, number, '123', 'user'):
#     utils.create_api_response(200, 'Testing - user saved in db')
# else:
#     utils.create_api_response(400, 'Failed to save user message to db')

# Test fetching of chat history
# chat_history = aws.get_chat_history(number)
# utils.create_api_response(200, f'Testing - chat history: {json.dumps(chat_history)}')

# Test saving in db
# if aws.save_in_db(DUMMY_MESSAGE, number, '123', 'user'):
#     utils.create_api_response(200, 'Testing - message saved in db')
# else:
#     utils.create_api_response(400, 'Failed to save user message to db')

# Test if new message has arrived
# if aws.confirm_if_new_msg(number, <timestamp>):
#     utils.create_api_response(200, 'Testing - new message has been received')
# else:
#     utils.create_api_response(400, 'New message has not been received')

# Test changing user language
# if aws.change_user_language(number, 'english'):
#     language = aws.get_user_language(number)
#     utils.create_api_response(200, f'Testing - language changed to: {language}')
# else:
#     utils.create_api_response(400, 'Failed to change user language')

# Test fetching user language
# language = aws.get_user_language(number)
# utils.create_api_response(200, f'Testing - language: {language}')

# Test WhatsApp...

# Test the WhatsApp API
# send_template_message(WHATSAPP_RECIPIENT_WAID, final_message_content)

# Test welcome message: "Hi!"
# Test change language message: "Spanish"
# Test button change language (with a prefered language and without one)
# Test button fact check + cancel

# Test WhatsApp + FACT CHECKING

# Test button fact check + ready: "Olives make you fat"
# Test button fact check + add more + ready: "Breast milk is a very good substitute" + "for COVID-19 vaccines"

# -------------
# CLAIMS TO TEST
# Breast milk is a very good substitute for COVID-19 vaccines. FALSE
# Technically, since Ukraine never officially registered its borders with the United Nations, Russia has not committed any violation of international law by invading its territory. FALSE
# Groups of Pakistani students used Indian flags in order to escape from Ukraine during the Russian invasion. FALSE
# Health care costs per person in the U.S. are one of the highest in the developed world. TRUE
# Image1 FALSE
# Image2 FALSE
# Image3 FALSE
# Image4 TRUE
# Image5 FALSE
# Image6 FALSE
# Image7 FALSE
