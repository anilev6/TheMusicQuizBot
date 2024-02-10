from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import TimedOut, TelegramError

from handlers.teacher.done import done

from logs.mylogging import logger


async def error(update: Update, context: CallbackContext) -> None:
    # For callback queries
    if update.callback_query:
        await update.callback_query.answer("A callback error occurred", show_alert=True)
    # For regular messages
    elif update.message:
        await update.message.reply_text("A message error occurred")
    else:
        logger.error(f"Update {update} caused error {context.error}")


def handle_telegram_timeout_errors(handler_function):
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            return await handler_function(update, context, *args, **kwargs)
        except TimedOut:
            logger.error(f"TimeOut: {handler_function.__name__}")
            return await done(update, context)
        except TelegramError as e:
            logger.error(
                f"Query is too old or invalid\nresponse timeout expired or query id is invalid: {handler_function.__name__}"
            )
            return await done(update, context)
        except Exception as e:
            logger.error(f"Unknown error:{handler_function.__name__}\n{e}\n")
            return await done(update, context)

    return wrapper
