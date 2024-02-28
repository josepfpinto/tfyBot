"""Testing"""
import os
from lib.whatsapp import send_template_message
from dotenv import load_dotenv

load_dotenv()
cost_info = []
DUMMY_MESSAGE = "Eu chamo-me José"

WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
print(send_template_message(WHATSAPP_RECIPIENT_WAID))
