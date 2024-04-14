"""Resolvers"""

import os
import json
from flask import request, Blueprint
from dotenv import load_dotenv
from lib import main_logic, utils, logger, aws
from lib.whatsapp import whatsapp
from lib.whatsapp.security import signature_required

this_logger = logger.configure_logging("RESOLVERS")

# Load environment variables
load_dotenv()
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
webhook_blueprint = Blueprint("webhook", __name__)


@webhook_blueprint.route("/", methods=["GET"])
def welcome():
    """API welcome resolver"""
    return utils.create_api_response(
        200, "Hello World! Welcome to Think for Yourself Bot."
    )


@webhook_blueprint.route("/test", methods=["GET"])
def test():
    """API test resolver - replace content with your own test"""
    return utils.create_api_response(
        200, f"Testing - WHATSAPP_VERIFY_TOKEN: {WHATSAPP_VERIFY_TOKEN}"
    )


@webhook_blueprint.route("/webhook", methods=["GET"])
@signature_required
def webhook_get():
    """token confirmation resolver"""
    # Parse params from the webhook verification request
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    # Check if a token and mode were sent
    if mode and token:
        # Check the mode and token sent are correct
        if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
            # Respond with 200 OK and challenge token from the request
            this_logger.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            # Responds with '403 Forbidden' if verify tokens do not match
            this_logger.info("VERIFICATION_FAILED")
            return utils.create_api_response(403, "Verification failed")
    else:
        # Responds with '400 Bad Request' if verify tokens do not match
        this_logger.info("MISSING_PARAMETER")
        return utils.create_api_response(400, "Missing parameters")


@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    """
    This resolver handles incoming webhook events from the WhatsApp API.

    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets
    processed. If the incoming payload is not a recognized WhatsApp event,
    an error is returned.

    Every message send will trigger 4 HTTP requests to your webhook: message, sent, delivered, read.

    Returns:
        response: A tuple containing a JSON response and an HTTP status code.
    """

    body = request.get_json()

    # Check if it's a WhatsApp status update
    if (
        body.get("entry", [{}])[0]
        .get("changes", [{}])[0]
        .get("value", {})
        .get("statuses")
    ):
        this_logger.info("Received a WhatsApp status update.")
        return utils.create_api_response(200, "")

    try:
        if whatsapp.is_valid_whatsapp_message(body):
            return main_logic.process_message(body)
        else:
            # if the request is not a WhatsApp API event, return an error
            return utils.create_api_response(404, "Not a WhatsApp API event")
    except json.JSONDecodeError:
        this_logger.error("Failed to decode JSON")
        return utils.create_api_response(400, "Invalid JSON provided")
