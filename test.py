"""Testing"""
import os
from lib.fact_check_logic import initial_fact_checking
from lib import gpt
from lib.whatsapp import send_template_message
from dotenv import load_dotenv

load_dotenv()
cost_info = []
DUMMY_MESSAGE = "Olives make you fat"
# WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
# print(send_template_message(WHATSAPP_RECIPIENT_WAID))

# Step 1: Initial Fact-Checking with Datasets/APIs
# TODO: improve focusing on wikipedia AND https://toolbox.google.com/factcheck/apis
fact_check_result = initial_fact_checking(DUMMY_MESSAGE, cost_info)

# Step 2: Advanced Analysis with PerplexityAPI OR CHATGPT(test temperature) WITH URLs
# TODO: Test, Review, Improve and Select
gpt4_request_with_web_search = gpt.gpt4_request_with_web_search(
    fact_check_result, cost_info, DUMMY_MESSAGE)

print('gpt4_request_with_web_search')
print(gpt4_request_with_web_search)
print(cost_info)
