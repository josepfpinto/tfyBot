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

        # Placeholder for Transcription of Images or Audio
        # TODO: Integrate media transcription services here

        # Placeholder for Language Translation
        # TODO: Detect language and translate if necessary

        response = fact_check_logic.process_fact_check_request(
            message, cost_info)
        print(response)
        aws.save_in_db(text, number, message_id, media_id, timestamp, response)
        whatsapp.send_message(response.deep_analysis)

        return 'enviado'

    except Exception as e:
        return 'no enviado ' + str(e)


if __name__ == '__main__':
    app.run()
