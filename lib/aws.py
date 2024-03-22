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


def save_in_db(message, number, message_id, media_id, timestamp):
    """ Function that saves data into messages, users and costs tables """
    # TODO: save message + sumup, user and costs - MESSAGES (id, phone number, threadId, message, cost)
    return


def get_last_user_message(number, timestamp, message_id):
    """ Function that gets last user messages """
    # TODO: fetch last 4 msg
    # if no sumup: create sumup with last 4 messages with timestamp 0.1s before to last message
    # save_in_db (sumup if created) plus last user_message (except interactive_messages)
    # return least of: last 4 msg OR last msg up to -including- sumup msg
    return []


def confirm_if_new_msg(number, timestamp):
    """ Function that confirms if a new message from the user has arrived """
    # TODO: check if last message timestamp is latter than current message timestamp
    return False


def get_user_language(number):
    """ Function that gets user prefered language. Returns the language in string or None. """
    # TODO: ...
    return None


def change_user_language(number, message):
    """ Function that changes the user prefered language. Returns true or false, depending on the request success. """
    # TODO: ...
    return True
