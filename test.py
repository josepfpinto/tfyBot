"""Testing"""
from langchain_core.messages import HumanMessage
import os
from lib.fact_check_logic import initial_fact_checking
from lib import gpt
from lib.whatsapp import send_template_message, send_message
from dotenv import load_dotenv
from lib.main_logic_graph import main_logic_graph

load_dotenv()
cost_info = []
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
number = '351xxxxxxxxx'

# print(send_message(number, 'test response 2', cost_info, 'text'))

# fact_check_result = initial_fact_checking(DUMMY_MESSAGE, cost_info)
# search_response = gpt.analyse_claim(
#     DUMMY_MESSAGE, fact_check_result, cost_info)
# print('search response')
# print(search_response)
# print(cost_info)


inputs = {"messages": [HumanMessage(content="what is the weather in lisbon?")]}
main_logic_graph.invoke(inputs)
