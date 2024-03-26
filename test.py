"""Testing"""
from langchain_core.messages import HumanMessage
import os
from lib.fact_check_logic import initial_fact_checking
from lib import gpt
from lib.whatsapp import send_template_message, send_message
from dotenv import load_dotenv
from fact_check_graph.start import main_logic_graph

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

inputs = "Search for the latest Ai technology in 2024, summarise the content. After summarising pass it on to insihgt researcher to provide insights for each topic."
# inputs = {"messages": [HumanMessage(content="Search for the latest Ai technology in 2024, summarise the content. After summarising pass it on to insihgt researcher to provide insights for each topic.")]}
main_logic_graph.invoke(inputs)
