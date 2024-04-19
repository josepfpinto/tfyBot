"""Testing"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from lib import utils, logger
from lib.whatsapp.whatsapp import send_template_message, send_message
from lib.fact_check_graph.start import graph

this_logger = logger.configure_logging("TEST")
load_dotenv()
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
number = "351xxxxxxxxx"

initial_state = {"messages": [HumanMessage(content=DUMMY_MESSAGE)], "history": []}
response = graph.invoke(initial_state)
final_message_content = response.get("messages")[0].content
this_logger.info("response: %s", response)
this_logger.info("final_message_content: %s", final_message_content)

# -------------
# Resolver /test

# Test environment variables - OK
# return utils.create_api_response(200, f'Testing - WHATSAPP_VERIFY_TOKEN: {WHATSAPP_VERIFY_TOKEN}')

# Test saving in db - OK
# this_logger.debug("starting")
# if aws.save_in_db('test message', '9xxxxxxxx', '123', 'user'):
#     this_logger.debug("message saved in db")
#     return utils.create_api_response(200, 'Testing - message saved in db')
# else:
#     this_logger.error("Failed to save message to db")
#     return utils.create_api_response(400, 'Failed to save message to db')

# Test fetching of chat history - OK
# this_logger.debug("starting")
# chat_history = aws.get_chat_history("9xxxxxxxx")
# return utils.create_api_response(
#     200,
#     f"Testing - chat history: {json.dumps(utils.langchain_message_to_dict(chat_history))}",
# )

# Test saving USER in db - OK
# this_logger.debug("starting")
# if aws.add_user('9xxxxxxxx'):
#     this_logger.debug("user saved in db")
#     return utils.create_api_response(200, 'Testing - user saved in db')
# else:
#     this_logger.error("Failed to save user message to db")
#     return utils.create_api_response(400, 'Failed to save user message to db')

# Test if new message has arrived - OK
# this_logger.debug("starting")
# from datetime import datetime
# older_date = datetime(2023, 12, 31, 23, 59, 59)
# if aws.confirm_if_new_msg("9xxxxxxxx", utils.get_timestamp(older_date)):
#     return utils.create_api_response(200, "Testing - new message has been received")
# else:
#     return utils.create_api_response(400, "New message has not been received")

# Test changing user language - OK
# this_logger.debug("starting")
# if aws.change_user_language("9xxxxxxxx", "english"):
#     language = aws.get_user_language("9xxxxxxxx")
#     return utils.create_api_response(
#         200, f"Testing - language changed to: {language}"
#     )
# else:
#     return utils.create_api_response(400, "Failed to change user language")

# Test fetching user language - OK
# this_logger.debug("starting")
# language = aws.get_user_language("9xxxxxxxx")
# return utils.create_api_response(200, f"Testing - language: {language}")

# -------------
# Test via WhatsApp

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
