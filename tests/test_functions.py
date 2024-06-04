"""Test functions"""

import json
import os
from datetime import datetime
from dotenv import load_dotenv
from tests.backend_request import RequestTypes, simmulate_message
from lib import utils, logger, aws

this_logger = logger.configure_logging("TEST_FUNCTIONS")
load_dotenv()
DUMMY_MESSAGE = "Olives make you fat"
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")
WHATSAPP_RECIPIENT_WAID = os.getenv("WHATSAPP_RECIPIENT_WAID")


def test_environment_variables():
    """Test environment variables"""
    this_logger.debug("starting test_environment_variables")
    this_logger.info(
        utils.create_api_response_for_test(
            200, f"Testing - WHATSAPP_VERIFY_TOKEN: {WHATSAPP_VERIFY_TOKEN}"
        )
    )


def test_saving_in_db():
    """Test saving in db"""
    this_logger.debug("starting test_saving_in_db")
    if aws.save_in_db("test message", WHATSAPP_RECIPIENT_WAID, "123", "user"):
        this_logger.info(
            utils.create_api_response_for_test(200, "Testing - message saved in db")
        )
    else:
        this_logger.info(
            utils.create_api_response_for_test(400, "Failed to save message to db")
        )


def test_saving_user():
    """Test saving user"""
    this_logger.debug("starting test_saving_user")
    if aws.add_user(WHATSAPP_RECIPIENT_WAID):
        this_logger.info(
            utils.create_api_response_for_test(200, "Testing - user saved in db")
        )
    else:
        this_logger.info(
            utils.create_api_response_for_test(400, "Failed to save user message to db")
        )


def test_fetching_of_chat_history():
    """Test fetching of chat history"""
    this_logger.debug("starting test_fetching_of_chat_history")
    chat_history = aws.get_chat_history(WHATSAPP_RECIPIENT_WAID)
    this_logger.info(
        utils.create_api_response_for_test(
            200,
            f"Testing - chat history: {json.dumps(utils.langchain_message_to_dict(chat_history))}",
        )
    )


def test_if_new_message_has_arrived():
    """Test if new message has arrived"""
    this_logger.debug("starting test_if_new_message_has_arrived")
    older_date = datetime(2023, 12, 31, 23, 59, 59)
    if aws.confirm_if_new_msg(WHATSAPP_RECIPIENT_WAID, utils.get_timestamp(older_date)):
        this_logger.info(
            utils.create_api_response_for_test(
                200, "Testing - new message has been received"
            )
        )
    else:
        this_logger.info(
            utils.create_api_response_for_test(400, "New message has not been received")
        )


def test_changing_user_language():
    """Test if new message has arrived"""
    this_logger.debug("starting test_changing_user_language")
    if aws.change_user_language(WHATSAPP_RECIPIENT_WAID, "english"):
        language = aws.get_user_language(WHATSAPP_RECIPIENT_WAID)
        this_logger.info(
            utils.create_api_response_for_test(
                200, f"Testing - language changed to: {language}"
            )
        )
    else:
        this_logger.info(
            utils.create_api_response_for_test(400, "Failed to change user language")
        )


def test_get_user_language():
    """Test fetching user language"""
    this_logger.debug("starting test_get_user_language")
    language = aws.get_user_language(WHATSAPP_RECIPIENT_WAID)
    this_logger.info(
        utils.create_api_response_for_test(200, f"Testing - language: {language}")
    )


def test_fetching_user_language():
    """Test fetching user language"""
    this_logger.debug("starting test_fetching_user_language")
    language = aws.get_user_language(WHATSAPP_RECIPIENT_WAID)
    this_logger.info(
        utils.create_api_response_for_test(200, f"Testing - language: {language}")
    )


def test_welcome_message():
    """Test welcome message"""
    this_logger.debug("starting test_welcome_message")
    this_logger.info(simmulate_message())


def test_greeting_message():
    """Test greeting user message"""
    this_logger.debug("starting test_greeting_message")
    this_logger.info(simmulate_message(RequestTypes.TEXT, "Hi!"))


def test_changing_language(language="Spanish"):
    """Test changing language"""
    this_logger.debug("starting test_changing_language")
    this_logger.info(simmulate_message(RequestTypes.TEXT, language))
