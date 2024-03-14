"""Testing"""
import os
from lib.fact_check_logic import initial_fact_checking
from lib import gpt
from lib.whatsapp import send_template_message, send_message
from dotenv import load_dotenv

load_dotenv()
cost_info = []
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
number = '351xxxxxxxxx'
print(send_message(number, 'test response 2'))

# fact_check_result = initial_fact_checking(DUMMY_MESSAGE, cost_info)
# search_response = gpt.analyse_claim(
#     DUMMY_MESSAGE, fact_check_result, cost_info)
# print('search response')
# print(search_response)
# print(cost_info)
