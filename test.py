"""Testing"""
import os
from lib.fact_check_logic import initial_fact_checking
from lib import gpt, perplexity
from lib.whatsapp import send_template_message
from dotenv import load_dotenv
from lib.utils import ANALYSE_USER_MESSAGE

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

search_response = gpt.gpt4_request_with_web_search_premium(
    ANALYSE_USER_MESSAGE, DUMMY_MESSAGE, fact_check_result, cost_info)

print('search response')
print(search_response)
print(cost_info)
