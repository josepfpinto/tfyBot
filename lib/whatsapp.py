"""Whatsapp related functions"""
import logging
import json
import os
import re
from dotenv import load_dotenv
import requests
from . import utils

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


def process_text_for_whatsapp(text):
    """Prepare message for whatsapp"""
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )


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
        logging.info("sending... %s to %s", data, whatsapp_url)
        data_json = json.dumps(data)
        response = requests.post(whatsapp_url,
                                 headers=headers,
                                 data=data_json,
                                 timeout=20)

        if response.status_code == 200:
            return utils.create_api_response(200, 'message sent')
        else:
            return utils.create_api_response(400, response.text)
    except Exception as e:
        return e, 403


def send_message(recipient, message):
    """send message to Whatsapp"""
    try:
        final_data = json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient,
                "type": "text",
                "text": {"preview_url": False, "body": process_text_for_whatsapp(message)},
            }
        )
        logging.info("sending...  %s to %s",  final_data, whatsapp_url)
        response = requests.post(whatsapp_url,
                                 headers=headers,
                                 data=final_data,
                                 timeout=20)

        return utils.create_api_response(response.status_code, 'message sent' if response.status_code == 200 else response.text)

    except Exception as e:
        return utils.create_api_response(403, e)
