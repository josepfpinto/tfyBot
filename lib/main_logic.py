"""main bot logic"""
import logging
from . import whatsapp, aws, fact_check_logic, gpt, utils


# List to store cost information
cost_info = []
DUMMY_MESSAGE = "olives make you fat"


def process_message(body):
    """function that process """
    entry = body['entry'][0]
    changes = entry['changes'][0]
    value = changes['value']
    message = value['messages'][0]
    number = message['from']
    message_id = message['id']
    timestamp = int(message['timestamp'])
    final_message, media_id = whatsapp.get_message(message)

    try:

        if aws.is_repeted_message(message_id):  # TODO
            return utils.create_api_response(200, 'repeated message')

        # Placeholder Step 1: Confirm what type of message it is:
        # TODO: 1.1 New number (confirm against dynamoDB)
        # TODO: 1.2 Confirm if it is the definition of preferred language (by keyword?) OR Request for institutional info (by keyword?) OR Continuation of previous conversation VS New factcheck request (depending if it is a new number or not and comparing to the time of previous messages - if it is more than 10min apart consider to be a new message).
        # TODO: 1.3 In case it can be the continuation of the conversation, use LLM to confirm which case.

        # Placeholder Step 2: Transcription of Images or Audio
        # TODO: Check for Media Type: Detect if the input is an image or audio file.
        # TODO: Transcription Service: Use a transcription API (from AWS?) to convert media to text.
        # Output: Transcribed text ready for further processing.

        # Placeholder Step 3: Language Translation
        translated_message = gpt.translate_with_gpt4_langchain(
            final_message, cost_info)

        # Placeholder Step 4: Confirm the type of LLM to be used, having into account the type of skills needed to answer (eg. websearch and text comprehension VS math)

        # Placeholder Step 5: Save data in DynamoDB Table:
        # TODO: 5.1 USERS (phone number, language) - if number still doesn't exist there
        # TODO: 5.2 MESSAGES (id, phone number, threadId, message, cost)

        # Step 6 / 7 / 8: Fact-Checking
        response = fact_check_logic.fact_check(
            translated_message['translated_message'], cost_info)
        logging.info(response)
        logging.info(cost_info)

        # Placeholder Step 9: Save data in DynamoDB Table:
        aws.save_in_db(translated_message['translated_message'],
                       number, message_id, media_id, timestamp, response)

        # Send message to user
        return whatsapp.send_message(number, 'test response')
        # return whatsapp.send_message(number, response['analysis_review'])

    except Exception as e:
        return utils.create_api_response(400, str(e))
