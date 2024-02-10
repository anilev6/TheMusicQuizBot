from telegram import Update
from telegram.ext import CallbackContext, MessageHandler, filters, ConversationHandler

from logs.mylogging import logger, time_log_decorator

from handlers.error import handle_telegram_timeout_errors


# States
REG_SURNAME, REG_NAME, REG_GROUP = range(2, 5)  # 0 is always data consent

# Constants
PARSE_MODE = "MarkdownV2"
TEXT1 = "Ласкаво просимо\!\nБудь ласка\, вкажіть своє прізвище\:"
TEXT2 = "ваше ім'я\:"
TEXT3 = "ваша група\:"
TEXT4 = "Дякую\!\nЩоб почати вікторину\, натисніть /start"


@time_log_decorator
@handle_telegram_timeout_errors
async def reg_start_student(update: Update, context: CallbackContext):
    # in case it's triggered by the callbackquery, it's better to send through the bot
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=TEXT1, parse_mode=PARSE_MODE
    )
    return REG_SURNAME


@time_log_decorator
@handle_telegram_timeout_errors
async def reg_surname(update: Update, context: CallbackContext):
    context.user_data["info"]["reg_last_name"] = update.message.text
    await update.message.reply_text(TEXT2, parse_mode=PARSE_MODE)
    return REG_NAME


@time_log_decorator
@handle_telegram_timeout_errors
async def reg_name(update: Update, context: CallbackContext):
    context.user_data["info"]["reg_first_name"] = update.message.text
    await update.message.reply_text(TEXT3, parse_mode=PARSE_MODE)
    return REG_GROUP


@time_log_decorator
@handle_telegram_timeout_errors
async def reg_group(update: Update, context: CallbackContext):
    """last stage"""
    context.user_data["info"]["reg_group"] = update.message.text
    # saving the data
    reg_info = context.user_data
    logger.info(f"A new user just registered : {update.effective_user.id} - {reg_info}")
    await update.message.reply_text(TEXT4, parse_mode=PARSE_MODE)
    return ConversationHandler.END


registration_states_student = {
    REG_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_surname)],
    REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_name)],
    REG_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_group)],
}
