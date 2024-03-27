"""main bot logic"""
from .fact_check_logic import fact_check_message
from . import aws, utils, gpt, logger
from whatsapp import whatsapp

this_logger = logger.configure_logging('MAIN')
DUMMY_MESSAGE = "olives make you fat"


def handle_text_message(number, message, language):
    """Handles processing of text messages."""
    this_logger.info('Processing text message.')
    chat_history = aws.get_chat_history(number)
    category = gpt.categorize_with_gpt4_langchain(message, chat_history)
    if category.get('value') == 'GREETINGS':
        this_logger.info('Greeting detected.')
        return whatsapp.send_message(number, '', 'interactive_welcome', language)
    elif category.get('value') == 'FACTCHECK':
        this_logger.info('Fact-check requested.')
        # Save message to DynamoDB here if necessary
        return whatsapp.send_message(number, '', 'interactive_more_menu', language)
    elif category.get('value') == 'LANGUAGE':
        this_logger.info('Language change requested.')
        if aws.change_user_language(number, message):
            language = aws.get_user_language(number)
            return whatsapp.send_message(number, 'Language changed.', 'interactive_main_menu', language)
        else:
            return whatsapp.send_message(number, "Sorry, wasn't able to change the language.", 'interactive_main_menu', language)
    else:
        return utils.create_api_response(400, f'Failed to categorize user message: {message} - category: {str(category)}')


def handle_interactive_message(number, interaction_id, message, message_id, media_id, timestamp, language):
    """Handles processing of interactive messages."""
    this_logger.info('Processing interactive message.')
    if interaction_id == "factcheck":
        return whatsapp.send_message(number, 'Ok then! Send your message and I’ll do my best to fact-check it. 😊', 'text', language)
    elif interaction_id == "buttonaddmore":
        return whatsapp.send_message(number, 'Ok, I’ll wait.', 'text', language)
    elif interaction_id == "buttonready":
        return fact_check_message(number, message_id, media_id, timestamp, language)
    elif interaction_id == "buttoncancel":
        return whatsapp.send_message(number, 'Ok. Anything else?', 'interactive_main_menu', language)
    elif interaction_id == "changelanguage":
        language_msg = f'''At the moment your preferred language is {
            language}. Please write your new preferred language.''' if language else "You don't have a preferred language. If you want, please write your preferred language."
        return whatsapp.send_message(number, language_msg, 'interactive_main_menu', language)
    # elif interaction_id == "moreinfo": TODO...
    else:
        return utils.create_api_response(400, f'Failed to identify interactive type: {message}')


def process_message(body):
    """Processes incoming WhatsApp messages for different interactions"""
    try:
        entry = body.get('entry')[0]
        changes = entry.get('changes')[0]
        value = changes.get('value')
        message = value.get('messages')[0]
        number = message.get('from')
        message_id = message.get('id')
        timestamp = int(message.get('timestamp'))
        final_message, media_id, interaction_id, type_message = whatsapp.get_message(
            message)
        this_logger.info(body)

        try:
            # Check for repeated messages
            if aws.is_repeted_message(message_id):
                return utils.create_api_response(200, 'repeated message')

            language = aws.get_user_language(number)
            this_logger.info('user language: %s', language)

            if type_message == 'text':
                return handle_text_message(number, final_message, language)
            elif type_message == 'interactive':
                return handle_interactive_message(number, interaction_id, message, message_id, media_id, timestamp, language)
            else:
                return utils.create_api_response(400, 'Unknown message type.')

            # Transcription of Images or Audio
            # TODO: Check for Media Type: Detect if the input is an image or audio file.
            # TODO: Transcription Service: Use a transcription API (from AWS?) to convert media to text.
            # Output: Transcribed text ready for further processing.

        except Exception as e:
            this_logger.error('Failed to process WhatsApp message: %s', e)
            return utils.create_api_response(400, str(e))

    except Exception as e:
        this_logger.error('Failed to parse WhatsApp message: %s', e)
        return utils.create_api_response(400, str(e))
