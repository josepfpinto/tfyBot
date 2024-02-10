"""AWS related functions"""

# DYNAMODB TABLES
# USERS (phone_number, language) - if number still doesn't exist there
# MESSAGES (message_id, phone_number, thread_id, message)
# COSTS (message_id, phone_number, cost, tokens)


def is_repeted_message(message_id):
    """ Function that checks if message_id exists in messages table """
    # TODO: add validation to avoid reprocess the same message,
    # in case the bot takes to much time to answer

    return False


def save_in_db(text, number, message_id, media_id, timestamp, response):
    """ Function that saves data into messages, users and costs tables """
    # TODO: save message, user and costs
    return
