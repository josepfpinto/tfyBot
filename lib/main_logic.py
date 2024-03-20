"""main bot logic"""
import logging
from .fact_check_logic import fact_check_message
from . import whatsapp, aws, utils, gpt

# List to store cost information
cost_info = []
DUMMY_MESSAGE = "olives make you fat"


def process_message(body):
    """function that process """
    try:
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        message_id = message['id']
        timestamp = int(message['timestamp'])
        final_message, media_id, interaction_id, type_message = whatsapp.get_message(
            message)
        logging.info(body)

        try:
            if aws.is_repeted_message(message_id):  # TODO
                return utils.create_api_response(200, 'repeated message')
            previous_user_messages = aws.get_last_user_message(
                number, timestamp, message_id)  # TODO

            if aws.confirm_if_new_msg(number, timestamp):  # TODO
                return utils.create_api_response(400, 'newer message exists')

            language = aws.get_user_language(number)  # TODO
            logging.info('text language: %s', language)

            if type_message == 'text':
                logging.info('text message')
                category = gpt.categorize_with_gpt4_langchain(
                    final_message,
                    cost_info,
                    previous_user_messages[-1] if previous_user_messages else 'None')
                if category.get('value') == 'GREETINGS':
                    logging.info('GREETINGS')
                    return whatsapp.send_message(number, '', cost_info, 'interactive_welcome', language)
                elif category.get('value') == 'FACTCHECK':
                    logging.info('FACTCHECK')
                    return whatsapp.send_message(number, '', cost_info, 'interactive_more_menu', language)
                elif category.get('value') == 'LANGUAGE':
                    logging.info('LANGUAGE')
                    if aws.change_user_language(number, language):
                        language = aws.get_user_language(number)
                        return whatsapp.send_message(number, 'Language changed', cost_info, 'interactive_main_menu', language)
                    else:
                        return whatsapp.send_message(number, "Sorry, wasn't able to change the language", cost_info, 'interactive_main_menu', language)
                else:
                    utils.create_api_response(400, f'''Failed to categorize user message: {
                        final_message} - category: {str(category)}''')

            elif type_message == 'interactive':
                logging.info('interactive message')
                if interaction_id == "factcheck":
                    return whatsapp.send_message(number,
                                                 '''Ok then! Send your message and I’ll do my best to fact check it. 😊''',
                                                 cost_info, 'text', language)
                elif interaction_id == "buttonaddmore":
                    return whatsapp.send_message(number, 'Ok, I’ll wait.', cost_info, 'text', language)
                elif interaction_id == "buttonready":
                    return fact_check_message(previous_user_messages,
                                              number,
                                              message_id,
                                              media_id,
                                              timestamp,
                                              cost_info,
                                              language)
                elif interaction_id == "buttoncancel":
                    return whatsapp.send_message(number, 'Ok. Anything else?', cost_info,
                                                 'interactive_main_menu', language)
                elif interaction_id == "changelanguage":
                    if language:
                        return whatsapp.send_message(number, f'''At the moment your prefered language is ${language}. Please write your new prefered language.''',
                                                     cost_info, 'interactive_main_menu', language)
                    return whatsapp.send_message(number, """You don't have a prefered language. If you want, please write your prefered language.""",
                                                 cost_info, 'interactive_main_menu', language)
                # elif interaction_id == "moreinfo": TODO...
                else:
                    utils.create_api_response(400, f'''Failed identify interactive type: {
                        final_message}''')

            # Transcription of Images or Audio
            # TODO: Check for Media Type: Detect if the input is an image or audio file.
            # TODO: Transcription Service: Use a transcription API (from AWS?) to convert media to text.
            # Output: Transcribed text ready for further processing.
        except Exception as e:
            return utils.create_api_response(400, str(e))
        finally:
            logging.info('cost_info: %s', cost_info)
    except Exception as e:
        logging.error('failed to parse whatsapp message')
        return utils.create_api_response(400, str(e))
