"""Testing"""
import logging
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from lib import gpt
from lib.whatsapp import send_template_message, send_message
from lib.fact_check_graph.start import graph

logging.basicConfig(level=logging.INFO)

load_dotenv()
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
number = '351xxxxxxxxx'

# print(send_message(number, 'test response 2', 'text'))

# fact_check_result = initial_fact_checking(DUMMY_MESSAGE)
# search_response = gpt.analyse_claim(
#     DUMMY_MESSAGE, fact_check_result)
# print('search response')
# print(search_response)

initial_state = {
    "messages": [HumanMessage(content=DUMMY_MESSAGE)],
    "history": []
}
response = graph.invoke(initial_state)
final_message_content = response.get("messages")[0].content
print('response: %s', response)
print('final_message_content: %s', final_message_content)
