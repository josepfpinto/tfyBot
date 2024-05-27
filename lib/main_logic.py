"""main bot logic"""

from lib.whatsapp import whatsapp
from lib.fact_check_logic import fact_check_message
from lib import aws, utils, gpt, logger

this_logger = logger.configure_logging("MAIN")
DUMMY_MESSAGE = "olives make you fat"


def check_if_last_message_is_waiting_for_continuation(chat_history):
    """Check if the last message in the chat history is waiting for continuation."""
    if not chat_history:
        # If the chat history is empty, return False
        return False

    # Get the last message in the chat history
    last_user_message = aws.get_user_message_from_history(chat_history)
    this_logger.debug("last_user_message: %s", last_user_message)

    # Check if the last message ends with '[cont.]'
    if last_user_message and last_user_message.content.endswith(
        utils.MESSAGE_TO_BE_CONTINUED_FLAG
    ):
        return True

    return False


def handle_text_message(number, message, language, message_id, timestamp):
    """Handles processing of text messages."""
    this_logger.info("\nProcessing text message.")
    chat_history = aws.get_chat_history(number)

    if check_if_last_message_is_waiting_for_continuation(chat_history):
        this_logger.info("Continuation of fact-check...")
        if aws.update_in_db(message, number, chat_history):
            this_logger.debug("Updated in DB")
            return whatsapp.send_message(number, "", "interactive_more_menu", language)

    category = gpt.categorize(message)
    if category.get("value") == "GREETINGS":
        this_logger.info("Greeting detected.")
        if aws.save_in_db(
            "Greeting detected.", number, message_id, "system", timestamp
        ):
            this_logger.debug("Saved in DB")
            return whatsapp.send_message(number, "", "interactive_welcome", language)
        return utils.create_api_response(400, "Failed to save system message to db")

    elif category.get("value") == "FACTCHECK":
        this_logger.info("Fact-check requested.")
        if aws.save_in_db(message, number, message_id, "user", timestamp, True):
            this_logger.debug("Saved in DB")
            return whatsapp.send_message(number, "", "interactive_more_menu", language)
        return utils.create_api_response(400, "Failed to save user message to db")

    elif category.get("value") == "LANGUAGE":
        this_logger.info("Language change requested.")
        if aws.save_in_db(
            "Language change requested.", number, message_id, "system", timestamp
        ):
            this_logger.debug("Saved in DB")
            if aws.change_user_language(number, message):
                this_logger.debug("Language Changed in DB")
                language = aws.get_user_language(number)
                this_logger.debug("Language fetched from DB %s", language)
                return whatsapp.send_message(
                    number, "Language changed.", "interactive_main_menu", language
                )
            else:
                return whatsapp.send_message(
                    number,
                    "Sorry, wasn't able to change the language.",
                    "interactive_main_menu",
                    language,
                )
        return utils.create_api_response(400, "Failed to save system message to db")

    else:
        return utils.create_api_response(
            400,
            f"Failed to categorize user message: {message} - category: {str(category)}",
        )


def handle_interactive_message(
    number, interaction_id, message, message_id, media_id, timestamp, language
):
    """Handles processing of interactive messages."""
    this_logger.info("\nProcessing interactive message.")

    if interaction_id == "factcheck":
        if aws.save_in_db(
            "ready to receive fact check message",
            number,
            message_id,
            "system",
            timestamp,
        ):
            this_logger.debug("Saved in DB")
            return whatsapp.send_message(
                number,
                "Ok then! Send your message and I’ll do my best to fact-check it. 😊",
                "text",
                language,
            )
        return utils.create_api_response(400, "Failed to save system message to db")

    elif interaction_id == "buttonaddmore":
        if aws.save_in_db(
            "waiting for next message", number, message_id, "system", timestamp
        ):
            this_logger.debug("Saved in DB")
            chat_history = aws.get_chat_history(number)
            if aws.wait_for_next_message(chat_history):
                return whatsapp.send_message(number, "Ok, I’ll wait.", "text", language)
            else:
                return whatsapp.send_message(
                    number,
                    "Sorry, won't allow the continuation of factcheck",
                    "interactive_main_menu",
                    language,
                )
        return utils.create_api_response(400, "Failed to save system message to db")

    elif interaction_id == "buttonready":
        if aws.save_in_db(
            "starting to fact check", number, message_id, "system", timestamp
        ):
            this_logger.debug("Saved in DB")
            return fact_check_message(number, message_id, media_id, timestamp, language)
        return utils.create_api_response(400, "Failed to save system message to db")

    elif interaction_id == "buttoncancel":
        if aws.save_in_db("cancel fact check", number, message_id, "system", timestamp):
            this_logger.debug("Saved in DB")
            return whatsapp.send_message(
                number, "Ok. Anything else?", "interactive_main_menu", language
            )
        return utils.create_api_response(400, "Failed to save system message to db")

    elif interaction_id == "changelanguage":
        if aws.save_in_db(
            "waiting for new language", number, message_id, "system", timestamp
        ):
            this_logger.debug("Saved in DB")
            language_msg = (
                f"""At the moment your preferred language is {
            language}. Please write your new preferred language."""
                if language
                else "You don't have a preferred language. If you want, please write your preferred language."
            )
            return whatsapp.send_message(
                number, language_msg, "interactive_main_menu", language
            )
        return utils.create_api_response(400, "Failed to save system message to db")

    # elif interaction_id == "moreinfo": TODO...
    else:
        return utils.create_api_response(
            400, f"Failed to identify interactive type: {message}"
        )


def process_message(body):
    """Processes incoming WhatsApp messages for different interactions"""
    try:
        entry = body.get("entry")[0]
        changes = entry.get("changes")[0]
        value = changes.get("value")
        message = value.get("messages")[0]
        number = message.get("from")
        message_id = message.get("id")
        timestamp = int(message.get("timestamp"))
        final_message, media_id, interaction_id, type_message = whatsapp.get_message(
            message
        )
        this_logger.info(body)

        this_logger.info("\n\n\n-----\n\nPROCESS MESSAGE: %s\n", final_message)
        this_logger.info("message_id %s", message_id)

        try:
            # Check for repeated messages
            if aws.is_repeted_message(message_id):
                return utils.create_api_response(200, "repeated message")

            language = aws.get_user_language(number)
            this_logger.debug("user language: %s", language)

            if type_message == "text":
                return handle_text_message(
                    number, final_message, language, message_id, timestamp
                )
            elif type_message == "interactive":
                return handle_interactive_message(
                    number,
                    interaction_id,
                    message,
                    message_id,
                    media_id,
                    timestamp,
                    language,
                )
            else:
                return utils.create_api_response(400, "Unknown message type.")

            # Transcription of Images or Audio
            # TODO: Check for Media Type: Detect if the input is an image or audio file.
            # TODO: Transcription Service: Use a transcription API (from AWS?) to convert media to text.
            # Output: Transcribed text ready for further processing.

        except Exception as e:
            this_logger.error("Failed to process WhatsApp message: %s", e)
            return utils.create_api_response(400, str(e))

    except Exception as e:
        this_logger.error("Failed to parse WhatsApp message: %s", e)
        return utils.create_api_response(400, str(e))
