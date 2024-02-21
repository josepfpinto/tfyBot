"""Main Function"""
import os
from lib import whatsapp, aws, fact_check_logic
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Load Flask
app = Flask(__name__)

# List to store cost information
cost_info = []
DUMMY_MESSAGE = "olives make you fat"


@app.route('/welcome', methods=['GET'])
def welcome():
    """ API welcome resolver """
    return 'Hello World! Welcome to Think for Yourslf Bot.'


@app.route('/webhook', methods=['GET'])
def check_token():
    """ token confirmation resolver """
    try:
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if token == TOKEN and challenge is not None:
            return challenge
        else:
            return 'incorrect token', 403
    except Exception as e:
        return e, 403


@app.route('/webhook', methods=['POST'])
def messages():
    """ main resolver """
    try:
        body = request.get_json()
        entry = body['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        message = value['messages'][0]
        number = message['from']
        message_id = message['id']
        timestamp = int(message['timestamp'])
        text, media_id = whatsapp.get_message(message)

        if aws.is_repeted_message(message_id):  # TODO
            return 'repeated message'

        # Placeholder Step 1: Confirm what type of message it is:
        # TODO: 1.1 New number (confirm against dynamoDB)
        # TODO: 1.2 Confirm if it is the definition of preferred language (by keyword?) OR Request for institutional info (by keyword?) OR Continuation of previous conversation VS New factcheck request (depending if it is a new number or not and comparing to the time of previous messages - if it is more than 10min apart consider to be a new message).
        # TODO: 1.3 In case it can be the continuation of the conversation, use LLM to confirm which case.

        # Placeholder Step 2: Transcription of Images or Audio
        # TODO: Check for Media Type: Detect if the input is an image or audio file.
        # TODO: Transcription Service: Use a transcription API (from AWS?) to convert media to text.
        # Output: Transcribed text ready for further processing.

        # Placeholder Step 3: Language Translation
        # TODO: Detect language and translate if necessary to english
        # Output: Text in English ready for fact-checking

        # Placeholder Step 4: Confirm the type of LLM to be used, having into account the type of skills needed to answer (eg. websearch and text comprehension VS math)

        # Placeholder Step 5: Save data in DynamoDB Table:
        # TODO: 5.1 USERS (phone number, language) - if number still doesn't exist there
        # TODO: 5.2 MESSAGES (id, phone number, threadId, message, cost)

        # Step 6 / 7 / 8: Fact-Checking
        response = fact_check_logic.fact_check(
            message, cost_info)
        print(response)
        print(cost_info)

        # Placeholder Step 9: Save data in DynamoDB Table:
        aws.save_in_db(text, number, message_id, media_id, timestamp, response)
        whatsapp.send_message(response.deep_analysis)

        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)


if __name__ == '__main__':
    app.run()
