from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from settings.settings import TG_BOT_TOKEN


# Define states
FIRST_STATE, SECOND_STATE = range(2)


# Initial command that sends the inline keyboard
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton(
                "Start Conversation", callback_data="trigger_conversation"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please click the button to start the conversation:", reply_markup=reply_markup
    )


# Entry point for the conversation triggered by a callback query
async def begin_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text="Conversation started. Please send your response."
    )
    return FIRST_STATE


# Handler for the first state of the conversation
async def handle_first_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    await update.message.reply_text(f"Received: {user_input}. Please send more input.")
    return SECOND_STATE


# Handler for the second state of the conversation
async def handle_second_state(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_input = update.message.text
    await update.message.reply_text(
        f"Final received: {user_input}. Conversation ended."
    )
    return ConversationHandler.END


# Setup the conversation handler with the callback query as an entry point
conv_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(begin_conversation, pattern="^trigger_conversation$")
    ],
    states={
        FIRST_STATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_first_state)
        ],
        SECOND_STATE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_second_state)
        ],
    },
    fallbacks=[CommandHandler("cancel", start)],  # Adjust the fallback as needed
)


def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
