from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
)

from handlers.teacher.main_menu import menu


async def done(update: Update, context: CallbackContext):
    await menu(update, context)
    return ConversationHandler.END


done_query_handler = CallbackQueryHandler(done, pattern="done")
done_command_handler = CommandHandler("done", done)
