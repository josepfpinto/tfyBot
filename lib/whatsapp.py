"""Whatsapp related functions"""
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_VERSION = os.getenv("WHATSAPP_VERSION")
WHATSAPP_APP_ID = os.getenv("WHATSAPP_APP_ID")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")

# 22-jul-2023 - WhatsApp supported types
MEDIA_TYPES = {
    'audio/aac': 'aac',
    'audio/mp4': 'mp4',
    'audio/mpeg': 'mp3',
    'audio/amr': 'amr',
    'audio/ogg': 'ogg',
    'video/mp4': 'mp4',
    'video/3gp': '3gp',
    'image/jpeg': 'jpeg',
    'image/png': 'png',
    'image/webp': 'webp',
    'text/plain': 'txt',
    'application/pdf': 'pdf',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/msword': 'doc',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
}

whatsapp_url = f"https://graph.facebook.com/{
    WHATSAPP_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer ' + WHATSAPP_TOKEN}


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


def send_template_message(recipient, template="hello_world"):
    """send template message to Whatsapp"""
    try:
        data = {
            "messaging_product": "whatsapp",
            "to": recipient,
            "type": "template",
            "template": {"name": template, "language": {"code": "en_US"}},
        }
        print("sending... ", data, whatsapp_url)
        data_json = json.dumps(data)
        response = requests.post(whatsapp_url,
                                 headers=headers,
                                 data=data_json,
                                 timeout=20)

        if response.status_code == 200:
            return 'message sent', 200
        else:
            return 'error while sending message', response.json()
    except Exception as e:
        return e, 403


def send_message(recipient, data):
    """send message to Whatsapp"""
    try:
        data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": data},
            }
        )
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
