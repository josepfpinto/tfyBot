"""Whatsapp template messages"""

from lib.whatsapp.whatsapp_interactions import filter_keys, options
from lib import utils, gpt, logger

exclude_keys = [""]

this_logger = logger.configure_logging("WHATSAPP_MESSAGES")


# def translate_option(option, language=None):
#     """Translate the option"""
#     this_logger.debug("Translating option")
#     if language:
#         this_logger.debug("Option: %s", option)
#         if "title" in option:
#             option["title"] = gpt.translate(option["title"], language)
#         if "reply" in option and "title" in option["reply"]:
#             option["reply"]["title"] = gpt.translate(option["reply"]["title"], language)
#     this_logger.debug("Translated option: %s", option)
#     return option


def get_main_menu():
    """Template: main menu options"""
    this_logger.debug("Getting main menu")
    return {
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
    }


def welcome_message(language=None):
    """Template: welcome message template"""

    body_text = "🤖 Hi! I’m an AI bot designed to be your informal fact checker, committed to Non-partisanship and Fairness, but without guarantees."
    footer_text = "What do you want to do? Check the menu."
    if language and "english" not in language.lower():
        body_text = gpt.translate(body_text, language)
        footer_text = gpt.translate(footer_text, language)

    this_logger.info("\nWelcome message: %s AND %s", body_text, footer_text)

    return {
        "type": "list",
        "header": {
            "type": "text",
            "text": "Think For Yourself Bot",
        },
        "body": {
            "text": body_text,
        },
        "footer": {
            "text": footer_text,
        },
        "action": get_main_menu(),
    }


def embed_main_menu(message):
    """Template: add main menu to message"""
    return {
        "type": "list",
        "body": {
            "text": message,
        },
        "action": get_main_menu(),
    }


def add_more_menu(language=None):
    """Template: ask the user to confirm if they want to add more info or not"""
    body_text = "Ready to fact check?"
    if language and "english" not in language.lower():
        body_text = gpt.translate(body_text, language)

    return {
        "type": "button",
        "body": {
            "text": body_text,
        },
        "action": {
            "buttons": [
                filter_keys(options["buttonready"], exclude_keys),
                filter_keys(options["buttonaddmore"], exclude_keys),
                filter_keys(options["buttoncancel"], exclude_keys),
            ],
        },
    }


def select_message_template(
    message_type, data, message="", source_language="english", target_language=None
):
    """Select a template for the message"""
    this_logger.info("\nSelecting message template in language %s", target_language)

    if (
        target_language
        and message
        and source_language.lower() not in target_language.lower()
    ):
        this_logger.debug(
            "\nTranslating from %s to %s", source_language, target_language
        )
        message = gpt.translate(message, target_language)

    if message_type == "text":
        this_logger.debug("Adding text message")
        data.update(
            {
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": utils.process_text_for_whatsapp(message),
                },
            }
        )
    elif message_type == "interactive_main_menu":
        this_logger.debug("Adding main menu")
        data.update(
            {
                "type": "interactive",
                "interactive": embed_main_menu(message),
            }
        )
    elif message_type == "interactive_more_menu":
        this_logger.debug("Adding more menu")
        data.update(
            {
                "type": "interactive",
                "interactive": add_more_menu(target_language),
            }
        )
    elif message_type == "interactive_welcome":
        this_logger.debug("Adding welcome message")
        data.update(
            {
                "type": "interactive",
                "interactive": welcome_message(target_language),
            }
        )
