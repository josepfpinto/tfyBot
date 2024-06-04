"""Backend request for testing"""

from datetime import datetime
from enum import Enum
import json
import base64
import copy
import os
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from lib import utils, logger

this_logger = logger.configure_logging("BACKEND_REQUEST")
load_dotenv()

IS_OFFLINE = os.getenv("IS_OFFLINE") == "true"
REMOTE_URL = os.getenv("REMOTE_URL")
LOCAL_URL = os.getenv("LOCAL_URL")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
WHATSAPP_TEST_NUMBER = os.getenv("WHATSAPP_TEST_NUMBER")

print("-------")
print("IS_OFFLINE: ", IS_OFFLINE)


class RequestTypes(Enum):
    """Request types"""

    WELCOME = 1
    TEXT = 2
    INTERACTIVE = 3


defult_body = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": WHATSAPP_BUSINESS_ACCOUNT_ID,
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": WHATSAPP_TEST_NUMBER,
                            "phone_number_id": WHATSAPP_PHONE_NUMBER_ID,
                        },
                        "contacts": [
                            {
                                "profile": {"name": "User 1"},
                                "wa_id": WHATSAPP_RECIPIENT_WAID,
                            }
                        ],
                        "messages": [
                            {
                                "from": WHATSAPP_RECIPIENT_WAID,
                                "id": "ID",
                                "timestamp": "TIMESTAMP",
                                "text": {"body": ""},
                                "type": "text",
                            }
                        ],
                    },
                    "field": "messages",
                }
            ],
        }
    ],
}


def build_interactive_body(timestamp, req_id, message):
    """Build interactive message body"""
    body = copy.deepcopy(defult_body)
    if message is None:
        message = ""
    message_dict = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_dict["timestamp"] = str(timestamp)
    message_dict["id"] = req_id
    message_dict["type"] = "interactive"
    message_dict["interactive"] = {
        "type": "button_reply",
        "button_reply": {"title": "", "id": message},
        "list_reply": {"title": "", "id": message},
        "document": {"text": message, "id": "MEDIA_ID"},
    }
    return body


def build_text_body(timestamp, req_id, message):
    """Build text message body"""
    body = copy.deepcopy(defult_body)
    if message is None:
        message = ""
    message_dict = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_dict["timestamp"] = str(timestamp)
    message_dict["id"] = req_id
    message_dict["text"]["body"] = message
    return body


def get_request_types(timestamp, req_id, message):
    """Get request types"""
    return {
        RequestTypes.WELCOME: {
            "type": "GET",
            "url": "/",
            "body": {},
        },
        RequestTypes.TEXT: {
            "type": "POST",
            "url": "/webhook",
            "body": build_text_body(timestamp, req_id, message),
        },
        RequestTypes.INTERACTIVE: {
            "type": "POST",
            "url": "/webhook",
            "body": build_interactive_body(timestamp, req_id, message),
        },
    }


def compute_signature(payload):
    """Compute the signature for a given body and secret"""
    hash_object = hmac.new(
        bytes(WHATSAPP_APP_SECRET, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    )
    return "sha256=" + hash_object.hexdigest()


def generate_random_id():
    """Generate a random ID"""
    random_bytes = os.urandom(30)  # Generate 30 random bytes
    base64_bytes = base64.b64encode(random_bytes)  # Encode the bytes in Base64
    base64_string = base64_bytes.decode()  # Convert the bytes to a string
    return "wamid." + base64_string + "="


def simmulate_message(
    req_type=RequestTypes.WELCOME,
    message=None,
    req_id=generate_random_id(),
):
    """Send a message to the backend for testing"""
    timestamp = int(datetime.now().timestamp())
    behaviour = get_request_types(timestamp, req_id, message)[req_type]
    url = (LOCAL_URL if IS_OFFLINE else REMOTE_URL) + behaviour["url"]
    request_type = behaviour["type"]
    payload = behaviour["body"]
    payload_json = json.dumps(payload, sort_keys=True)
    signature = compute_signature(payload_json)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
    }
    if request_type == "POST":
        headers["X-Hub-Signature-256"] = signature
    this_logger.debug("Payload: %s", payload)
    this_logger.debug("Headers: %s", headers)

    try:
        response = requests.request(
            request_type, url, headers=headers, data=payload_json, timeout=30
        )
        this_logger.debug("Response: %s", str(response))
        return utils.create_api_response_for_test(200, str(response.text))
    except Exception as e:
        this_logger.error("Failed to send message: %s", e)
        return utils.create_api_response_for_test(400, str(e))
