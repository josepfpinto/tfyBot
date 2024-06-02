import os
from functools import wraps
from flask import jsonify, request
import hashlib
import hmac
from dotenv import load_dotenv
from lib import logger

this_logger = logger.configure_logging("SECURITY")

# Load environment variables
load_dotenv()
WHATSAPP_APP_SECRET = os.getenv("WHATSAPP_APP_SECRET")
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
    this_logger.debug("Incoming payload:", payload)
    this_logger.debug("secret: %s", WHATSAPP_APP_SECRET)
    this_logger.debug("Signatures match:", signature == expected_signature)
    this_logger.debug(
        "Comparing incoming sigature: %s | WITH computed one: %s",
        signature,
        expected_signature,
    )

    # Check if the signature matches
    return hmac.compare_digest(expected_signature, signature)


def signature_required(f):
    """
    Decorator to validate the signature of incoming requests
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.headers.get("X-Hub-Signature-256", "")[
            7:
        ]  # Removing 'sha256='

        if not validate_signature(request.data.decode("utf-8"), signature):
            this_logger.info("Signature verification failed!")
            return jsonify({"status": "error", "message": "Invalid signature"}), 403

        return f(*args, **kwargs)

    return decorated_function
