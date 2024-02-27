"""Whatsapp related functions"""
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_URL = os.getenv('WHATSAPP_URL')


def get_message(message):
    """parse Whatsapp message"""
    media_id = ''
    text = 'Message not recognized'
    type_message = message.get('type', '')

    if type_message == 'text':
        text = message['text']['body']
    elif type_message == 'document':
        media_id = message[type_message]['id']
        text = message[type_message].get('filename', '')
    else:
        text = 'Message not processed'
    return text, media_id


def send_message(data):
    """send message to Whatsapp"""
    try:
        whatsapp_token = WHATSAPP_TOKEN
        whatsapp_url = WHATSAPP_TOKEN
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'Bearer ' + whatsapp_token}
        print("sending... ", data)
        response = requests.post(whatsapp_url,
                                 headers=headers,
                                 data=data,
                                 timeout=20)

        if response.status_code == 200:
            return 'message sent', 200
        else:
            return 'error while sending message', response.status_code
    except Exception as e:
        return e, 403
