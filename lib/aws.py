"""AWS related functions"""
import os
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key
from lib.gpt import summarize_with_gpt3_langchain
from lib import utils, logger

this_logger = logger.configure_logging('AWS')

# Load environment variables
load_dotenv()
USERS_TABLE = os.getenv('USERS_TABLE')
SESSIONS_TABLE = os.getenv("SESSIONS_TABLE")
IS_OFFLINE = os.getenv("IS_OFFLINE") == "true"

# DYNAMODB TABLES
# UsersTable (phone_number:key-string, language:string)
# SessionTable (message_id:key-string, session_id(phone_number:string), message:string, type:'bot'|'user'|'sumup', timestamp:Unix timestamp format))
# SessionIdTimestampIndex: Global Secondary Index (GSI) with session_id as the partition key and timestamp as the sort key

dynamodb = boto3.resource('dynamodb')
sessionTable = dynamodb.Table(SESSIONS_TABLE)
usersTable = dynamodb.Table(USERS_TABLE)

if IS_OFFLINE:
    dynamodb = boto3.resource(
        'dynamodb',
        region_name='localhost',
        endpoint_url='http://localhost:8080',
        aws_access_key_id='fakeMyKeyId',
        aws_secret_access_key='fakeSecretAccessKey'
    )


def get_chat_history(session_id):
    """ Function that gets last user messages """
    try:
        response = sessionTable.query(
            IndexName='SessionIdTimestampIndex',
            KeyConditionExpression=Key('session_id').eq(session_id),
            ScanIndexForward=False  # Fetch latest messages first
        )
        this_logger.debug('response %s', response)

        messages = response['Items']

        if not messages:  # If it's a new user with no messages
            this_logger.debug('no messages...')
            return None

        formatted_history = []
        sumup_found = False
        total_chars = 0

        # Process messages in reverse order to maintain chronological order after breaking for sumup
        for message in reversed(messages):
            # Decide message type and format accordingly
            this_logger.debug('message %s', message)
            if message['type'] == 'bot':
                this_logger.debug('type bot')
                formatted_message = AIMessage(
                    content=message['message'], name='Fact_Checker')
            elif message['type'] == 'sumup':
                this_logger.debug('type sumup')
                formatted_message = SystemMessage(
                    content=message['message'], name='System')
                sumup_found = True  # Mark that a sumup message was found
            elif message['type'] == 'user':
                this_logger.debug('type user')
                formatted_message = HumanMessage(
                    content=message['message'], name='User')
            else:
                this_logger.debug('no known type found...')
                # Handle unexpected message types if necessary
                continue

            formatted_history.append(formatted_message)
            total_chars += len(message['message'])

            # Break the loop if a sumup message was found
            if sumup_found:
                break

        this_logger.debug('formatted_history %s', formatted_history)

        # If no sumup message was found, limit the history to the last 4 messages
        if not sumup_found:
            this_logger.debug('no sumup found...')
            formatted_history = formatted_history[-4:]

        # Check if the total character count exceeds the limit
        if total_chars > utils.HISTORY_CHAR_LIMMIT:
            this_logger.debug('total_chars %s > utils.HISTORY_CHAR_LIMMIT %s',
                              total_chars, utils.HISTORY_CHAR_LIMMIT)
            original_messages = [
                f"{msg.get('type')}: {msg.get('message')}" for msg in messages]
            summary = summarize_with_gpt3_langchain(
                '; '.join(original_messages), utils.HISTORY_CHAR_LIMMIT)
            formatted_history = [SystemMessage(content=summary, name='System')]

        this_logger.debug('formatted_history %s', formatted_history)
        return formatted_history
    except Exception as e:
        this_logger.error(
            "Error fetching chat history for session_id %s: %s", session_id, e)
        return None


def is_repeted_message(message_id):
    """Checks if message_id exists in SessionTable."""
    try:
        response = sessionTable.get_item(Key={'message_id': message_id})
        this_logger.debug('response %s', response)
        return 'Item' in response
    except Exception as e:
        this_logger.error("Error checking if message is repeated: %s", e)
        return False


def save_in_db(message, number, message_id, message_type='bot', timestamp=utils.get_timestamp()):
    """Saves message data into SessionTable."""
    try:
        sessionTable.put_item(Item={
            'message_id': message_id,
            'session_id': number,
            'message': message,
            'timestamp': timestamp,
            'type': message_type
        })
        return True
    except Exception as e:
        this_logger.error("Error saving message: %s", e)
        return False


def confirm_if_new_msg(number, current_message_timestamp):
    """Checks if the last message timestamp is later than the current message timestamp."""
    try:
        response = sessionTable.query(
            IndexName='SessionIdTimestampIndex',
            KeyConditionExpression=Key('session_id').eq(number),
            ScanIndexForward=False,  # Latest messages first
            Limit=1  # Only fetch the most recent message
        )
        this_logger.debug('response %s', response)

        if not response['Items']:
            this_logger.debug('no items...')
            return False

        last_message_timestamp = int(response['Items'][0]['timestamp'])
        has_new_message = last_message_timestamp > current_message_timestamp
        this_logger.debug('has_new_message %s = last_message_timestamp %s > current_message_timestamp %s',
                          has_new_message, last_message_timestamp, current_message_timestamp)

        if has_new_message:
            this_logger.info("A more recent message exists. Stopping process.")

        return has_new_message
    except Exception as e:
        this_logger.error("Error checking if there is a new message: %s", e)
        return False


def get_user_language(number):
    """Gets the user's preferred language."""
    try:
        response = usersTable.get_item(Key={'phone_number': number})
        this_logger.debug('response %s', response)
        if 'Item' in response:
            return response['Item'].get('language', None)

        this_logger.debug('no item...')
        return None
    except Exception as e:
        this_logger.error("Error fetching user language: %s", e)
        return None


def change_user_language(number, new_language):
    """Changes the user's preferred language."""
    try:
        usersTable.update_item(
            Key={'phone_number': number},
            UpdateExpression='SET language = :val',
            ExpressionAttributeValues={':val': new_language}
        )
        this_logger.info("Language updated for %s.", number)
        return True
    except Exception as e:
        this_logger.error("Error updating language for %s: %s", number, e)
        return False


def add_user(phone_number):
    """Adds a new user with no preferred language."""
    try:
        usersTable.put_item(Item={
            'phone_number': phone_number,
            'language': None  # Indicates no preferred language set
        })
        this_logger.info("User %s added successfully.", phone_number)
        return True
    except Exception as e:
        this_logger.error("Error adding user %s: %s", phone_number, e)
        return False
