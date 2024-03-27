"""Whatsapp template messages"""
import re
from .whatsapp_interactions import filter_keys, options

exclude_keys = ['']


def process_text_for_whatsapp(text):
    """Prepare message for whatsapp"""
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def get_main_menu():
    """Template: main menu options"""
    return ({
        "button": "Menu",
        "sections": [
            {
                # "title": "",
                "rows": [
                    filter_keys(options["factcheck"], exclude_keys),
                    # filter_keys(options["moreinfo"], exclude_keys),
                    filter_keys(options["changelanguage"], exclude_keys),
                ],
            },
        ],
    })


def welcome_message():
    """Template: welcome message template"""
    return ({
        "type": "list",
        "header": {
            "type": "text",
            "text": "Think For Yourself Bot",
        },
        "body": {
            "text": "🤖 Hi! I’m an AI bot designed to be your informal fact checker, committed to Non-partisanship and Fairness, but without guarantees.",
        },
        "footer": {
            "text": "What do you want to do? Check the menu.",
        },
        "action": get_main_menu(),
    })


def embed_main_menu(message):
    """Template: add main menu to message"""
    return ({
        "type": "list",
        "body": {
            "text": message,
        },
        "action": get_main_menu(),
    })


def add_more_menu():
    """Template: ask the user to confirm if they want to add more info or not"""
    return ({
        "type": "button",
        "body": {
            "text": 'Ready to fact check?',
        },
        "action": {
            "buttons": [
                filter_keys(options["buttonready"], exclude_keys),
                filter_keys(options["buttonaddmore"], exclude_keys),
                filter_keys(options["buttoncancel"], exclude_keys),
            ],
        },
    })


def select_message_template(message_type, data, message=''):
    """Select a template for the message"""
    if message_type == 'text':
        data.update(
            {
                "type": 'text',
                "text": {"preview_url": False, "body": process_text_for_whatsapp(message)},
            }
        )
    elif message_type == 'interactive_main_menu':
        data.update(
            {
                "type": 'interactive',
                "interactive": embed_main_menu(message),
            }
        )
    elif message_type == 'interactive_more_menu':
        data.update(
            {
                "type": 'interactive',
                "interactive": add_more_menu(),
            }
        )
    elif message_type == 'interactive_welcome':
        data.update(
            {
                "type": 'interactive',
                "interactive": welcome_message(),
            }
        )
