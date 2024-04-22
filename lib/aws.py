"""AWS related functions"""

import os
from decimal import Decimal
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.conditions import Key, Attr
from lib.gpt import summarize_with_gpt3_langchain
from lib import utils, logger
from gensim.models import Word2Vec
from scipy import spatial

this_logger = logger.configure_logging("AWS")

# Load environment variables
load_dotenv()
USERS_TABLE = os.getenv("USERS_TABLE")
SESSIONS_TABLE = os.getenv("SESSIONS_TABLE")
IS_OFFLINE = os.getenv("IS_OFFLINE") == "true"

# DYNAMODB TABLES
# UsersTable (phone_number:key-string, language:string)
# SessionTable (message_id:key-string, vector:string, session_id(phone_number:string), message:string, type:'system'|'bot'|'user'|'sumup', timestamp:Unix timestamp format))
# SessionIdTimestampIndex: Global Secondary Index (GSI) with session_id as the partition key and timestamp as the sort key

dynamodb = boto3.resource("dynamodb")
sessionTable = dynamodb.Table(SESSIONS_TABLE)
usersTable = dynamodb.Table(USERS_TABLE)

if IS_OFFLINE:
    dynamodb = boto3.resource(
        "dynamodb",
        region_name="localhost",
        endpoint_url="http://localhost:8080",
        aws_access_key_id="fakeMyKeyId",
        aws_secret_access_key="fakeSecretAccessKey",
    )


def vectorize(message):
    """Vectorize message"""
    # Load the model
    model = Word2Vec.load("word2vec.model")

    # Convert claim into a vector
    claim_vector = model.wv[message]

    return claim_vector


def get_chat_history(session_id):
    """Function that gets last user messages"""
    try:
        this_logger.info("\nget_chat_history")
        response = sessionTable.query(
            IndexName="SessionIdTimestampIndex",
            KeyConditionExpression=Key("session_id").eq(session_id),
            ScanIndexForward=False,  # Fetch latest messages first
        )

        messages = response["Items"]

        if not messages:  # If it's a new user with no messages
            this_logger.debug("no messages...")
            return None

        formatted_history = []
        sumup_found = False
        total_chars = 0

        # Process messages in reverse order to maintain chronological order after breaking for sumup
        for message in messages:
            # Decide message type and format accordingly
            this_logger.debug("message %s", message)
            if message["type"] == "system":
                this_logger.debug("type system")
                continue  # Skip system messages
            if message["type"] == "bot":
                this_logger.debug("type bot")
                formatted_message = AIMessage(
                    content=message["message"], name="Fact_Checker", id=message["message_id"]
                )
            elif message["type"] == "sumup":
                this_logger.debug("type sumup")
                formatted_message = SystemMessage(
                    content=message["message"], name="System", id=message["message_id"]
                )
                sumup_found = True  # Mark that a sumup message was found
            elif message["type"] == "user":
                this_logger.debug("type user")
                formatted_message = HumanMessage(
                    content=message["message"], name="User", id=message["message_id"]
                )
            else:
                this_logger.debug("no known type found...")
                # Handle unexpected message types if necessary
                continue

            formatted_history.append(formatted_message)
            total_chars += len(message["message"])

            # Break the loop if a sumup message was found
            if sumup_found:
                break

        # If no sumup message was found, limit the history to the most recent 4 messages
        if not sumup_found:
            this_logger.debug("no sumup found...")
            formatted_history = formatted_history[-4:]

        # Check if the total character count exceeds the limit
        if total_chars > utils.HISTORY_CHAR_LIMMIT:
            original_messages = utils.message_to_dict(messages)
            summary = summarize_with_gpt3_langchain(
                "; ".join(original_messages), utils.HISTORY_CHAR_LIMMIT
            )
            formatted_history = [SystemMessage(content=summary, name="System")]

        this_logger.debug("formatted_history %s", formatted_history)
        return formatted_history
    except Exception as e:
        this_logger.error(
            "Error fetching chat history for session_id %s: %s", session_id, e
        )
        return None


def is_repeted_message(message_id):
    """Checks if message_id exists in SessionTable."""
    this_logger.info("is_repeted_message: %s", message_id)
    try:
        response = sessionTable.get_item(Key={"message_id": message_id})
        this_logger.debug("response %s", response)
        return "Item" in response
    except Exception as e:
        this_logger.error("Error checking if message is repeated: %s", e)
        return False


def save_in_db(
    message, number, message_id, message_type="bot", timestamp=utils.get_timestamp(), to_vectorize=False
):
    """Saves message data into SessionTable."""
    try:
        this_logger.debug('\nSaving message "%s" for %s.', message, number)
        sessionTable.put_item(
            Item={
                "message_id": message_id,
                "session_id": number,
                "message": message,
                "timestamp": timestamp,
                "type": message_type,
                "vector": vectorize(message) if to_vectorize else "",
            }
        )
        return True
    except Exception as e:
        this_logger.error("Error saving message: %s", e)
        return False


def get_latest_message(number):
    """Retrieve the latest message for a given number from SessionTable."""
    response = sessionTable.query(
        IndexName='SessionIdTimestampIndex',
        KeyConditionExpression=Key('session_id').eq(number),
        ScanIndexForward=False,  # This makes the query return results in descending order of sort key
        Limit=1  # We only need the latest item
    )
    return response['Items'][0] if response['Items'] else None


def update_message(message, message_id):
    """Update a message for a given number from SessionTable."""
    this_logger.info('\nUpdating message with %s for %s', message, message_id)

    # Convert claim into a vector
    claim_vector = vectorize(message)

    sessionTable.update_item(
        Key={
            'message_id': message_id
        },
        UpdateExpression='SET message = :val1, SET vector = :val2',
        ExpressionAttributeValues={
            ':val1': message,
            ':val2': claim_vector
        }
    )


def wait_for_next_message(chat_history):
    """Updates the latest message of a particular number in SessionTable with MESSAGE_TO_BE_CONTINUED_FLAG."""
    try:
        this_logger.info('\nUpdating latest message with MESSAGE_TO_BE_CONTINUED_FLAG.')

        user_message = get_user_message_from_history(chat_history)

        if user_message:
            new_message = user_message.content + ' ' + utils.MESSAGE_TO_BE_CONTINUED_FLAG

            update_message(new_message, user_message.id)

        return True
    except Exception as e:
        this_logger.error("Error updating message: %s", e)
        return False


def get_user_message_from_history(chat_history):
    """Function to get the user message from the chat history"""
    try:
        this_logger.info("Getting user message from chat history")
        message = next((msg for msg in chat_history if isinstance(msg, HumanMessage) and msg.name == 'User'), None)
        this_logger.debug("User message: %s", message.content)
        return message

    except Exception as e:
        this_logger.error("Error getting user message from chat history: %s", e)
        return None


def update_in_db(message, number, chat_history):
    """Updates the latest message of a particular number in SessionTable."""
    try:
        this_logger.info('\nUpdating latest message with "%s" for %s.', message, number)

        old_message = get_user_message_from_history(chat_history)

        if old_message:
            message_update = old_message.content

            # Check if the current message ends with utils.MESSAGE_TO_BE_CONTINUED_FLAG
            if message_update.endswith(utils.MESSAGE_TO_BE_CONTINUED_FLAG):
                # If it does, remove utils.MESSAGE_TO_BE_CONTINUED_FLAG and append the new message
                message_update = message_update[:-len(utils.MESSAGE_TO_BE_CONTINUED_FLAG)] + message
            else:
                # If it doesn't, just append the new message
                message_update += message

            update_message(message_update, old_message.id)

        return True
    except Exception as e:
        this_logger.error("Error updating message: %s", e)
        return False


def confirm_if_new_msg(number, current_message_timestamp):
    """Checks if the last message timestamp is later than the current message timestamp."""
    this_logger.info("\nconfirm_if_new_msg %s", number)
    current_item = get_latest_message(number)

    if current_item:
        last_message_timestamp = Decimal(current_item["timestamp"])
        has_new_message = last_message_timestamp > current_message_timestamp
        this_logger.debug(
            "has_new_message %s = last_message_timestamp %s > current_message_timestamp %s",
            has_new_message,
            last_message_timestamp,
            current_message_timestamp,
        )

        if has_new_message:
            this_logger.info("A more recent message exists: %s. Stopping process.", current_item.get("message"))

        return has_new_message

    else:
        return False


def get_user_language(number):
    """Gets the user's preferred language."""
    this_logger.info("\nget_user_language")
    try:
        response = usersTable.get_item(Key={"phone_number": number})
        this_logger.debug("response %s", response)
        if "Item" in response:
            return response["Item"].get("language", None)
        return None
    except Exception as e:
        this_logger.error("Error fetching user language: %s", e)
        return None


def change_user_language(number, new_language):
    """Changes the user's preferred language."""
    this_logger.info("\nchange_user_language %s to %s", number, new_language)
    try:
        usersTable.update_item(
            Key={"phone_number": number},
            UpdateExpression="SET #lang = :val",
            ExpressionAttributeNames={"#lang": "language"},
            ExpressionAttributeValues={":val": new_language},
        )
        return True
    except Exception as e:
        this_logger.error("Error updating language for %s: %s", number, e)
        return False


def add_user(phone_number):
    """Adds a new user with no preferred language."""
    this_logger.info("\nadd_user %s", phone_number)
    try:
        usersTable.put_item(
            Item={
                "phone_number": phone_number,
                "language": None,  # Indicates no preferred language set
            }
        )
        return True
    except Exception as e:
        this_logger.error("Error adding user %s: %s", phone_number, e)
        return False


def check_for_simmilar_claims(message):
    """Function to compare a claim vector with existing claim vectors"""
    try:
        # Convert claim into a vector
        claim_vector = message.additional_kwargs["vector"]

        # Query DynamoDB table to retrieve vectors of all existing claims
        # these only exist on user type messages and have a vector string
        response = sessionTable.query(
            IndexName="TypeVectorIndex",
            KeyConditionExpression=Key("type").eq("user"),
            FilterExpression=Attr("vector").exists(),
        )

        # Find the most similar claim
        most_similar_message = ""
        highest_similarity = -1
        for item in response.get("Items", []):
            if item["message_id"] == message.id:
                continue
            existing_vector = item.get("vector", "")
            similarity = 1 - spatial.distance.cosine(claim_vector, existing_vector)
            if similarity > highest_similarity:
                highest_similarity = similarity
                most_similar_message = item.get("message", "")

        # If the most similar claim is above a certain similarity threshold, fetch the answer
        if highest_similarity > 0.85:
            this_logger.info("A simmilar claim was found")
            return {'claim': most_similar_message,
                    'status': True}
        else:
            this_logger.info("No simmilar claim was found")
            return {'claim': "No similar claim was found",
                    'status': False}

    except Exception as e:
        this_logger.error("Error checking for simmilar claims: %s", e)
        return {'claim': "No similar claim was found",
                'status': False}
