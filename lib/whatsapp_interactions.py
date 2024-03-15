"""Whatsapp interactions"""


def filter_keys(item, exclude_keys):
    """Return a copy of the item dictionary with the specified keys excluded."""
    return {k: v for k, v in item.items() if k not in exclude_keys}


options = {
    "factcheck": {
        "id": "factcheck",
        "title": "Fact check a message",
    },
    "moreinfo": {
        "id": "moreinfo",
        "title": "More info about the bot",
    },
    "changelanguage": {
        "id": "changelanguage",
        "title": "Change language",
    },
    "buttonready": {
        "type": "reply",
        "reply": {
            "id": "buttonready",
            "title": "Ready!",
        }
    },
    "buttonaddmore": {
        "type": "reply",
        "reply": {
            "id": "buttonaddmore",
            "title": "Add more info",
        }
    },
    "buttoncancel": {
        "type": "reply",
        "reply": {
            "id": "buttoncancel",
            "title": "Cancel",
        }
    },
}
