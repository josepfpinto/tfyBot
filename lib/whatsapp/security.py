import os
from functools import wraps
from flask import jsonify, request
import hashlib
import hmac
from dotenv import load_dotenv
from lib import logger

this_logger = logger.configure_logging('SECURITY')

# Load environment variables
load_dotenv()
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET')
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")


def validate_signature(payload, signature):
    """
    Validate the incoming payload's signature against our expected signature
    """
    # Use the App Secret to hash the payload
    expected_signature = hmac.new(
        bytes(WHATSAPP_APP_SECRET, "latin-1"),
        msg=payload.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    this_logger.debug(expected_signature)
    this_logger.debug(signature)

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, signature)


def is_edit_webhook_request(request):
    """
    Check if the incoming request is for editing the webhook's callback URL
    """
    # Replace with the actual condition that determines if the request is for editing the webhook's callback URL
    return request.path == "/edit-webhook"


def signature_required(f):
    """
    Decorator to ensure that the incoming requests to our webhook are valid and signed with the correct signature.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        this_logger.debug(request)
        this_logger.debug(f"Request method: {request.method}")
        this_logger.debug(f"Request path: {request.path}")
        this_logger.debug(f"Request headers: {request.headers}")
        this_logger.debug(f"Request body: {request.data.decode('utf-8')}")
        signature = request.headers.get("X-Hub-Signature-256", "")[7:]  # Removing 'sha256='

        # If the request is for editing the webhook's callback URL, skip the signature validation
        # if is_edit_webhook_request(request):
        #     return f(*args, **kwargs)

        if not validate_signature(request.data.decode("utf-8"), signature):
            this_logger.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403

        return f(*args, **kwargs)

    return decorated_function
