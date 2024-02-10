from telegram.ext import MessageHandler, filters


# A dict to hold message handlers
MESSAGE_HANDLERS = {}


def message_handler(func):
    """
    A decorator to register a function as a command handler for a specific flag.
    """

    MESSAGE_HANDLERS[func.__name__] = MessageHandler(
        filters.TEXT & ~filters.COMMAND, func
    )

    return func


# Function to add all registered handlers to the application
def add_message_handlers(application):
    for handler in MESSAGE_HANDLERS.values():
        application.add_handler(handler)
