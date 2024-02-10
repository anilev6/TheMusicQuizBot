from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CallbackQueryHandler

from datetime import datetime


# Constants
PARSE_MODE = "MarkdownV2"
CONFIRM_QUESTION_TEXT = "*Продовжуючи\, ви надаєте згоду на збір та обробку деяких ваших персональних даних*"
CONFIRM_TEXT = "Ви надали свою згоду на збір та обробку даних\, дякую\."
NOT_CONFIRM_TEXT = "🙊🙉🙈"
CONFIRM_BUTTON = "Продовжити"
EXIT_BUTTON = "Вийти"

# States
DATA_CONSENT, DATA_CONSENT_OVER = range(2)  # reserver for these two states


async def get_data_consent(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(CONFIRM_BUTTON, callback_data="data_consent")],
        [InlineKeyboardButton(EXIT_BUTTON, callback_data="not_data_consent")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        CONFIRM_QUESTION_TEXT, reply_markup=reply_markup, parse_mode=PARSE_MODE
    )
    return DATA_CONSENT


def get_user_full_tg_info(user) -> dict:
    # Gather user info from telegram user object
    user_info = {
        "added_on": datetime.now(),
        "tg_username": f"@{user.username}" if user.username else "None",
        "tg_first_name": f"{user.first_name}" if user.first_name else "None",
        "tg_last_name": f"{user.last_name}" if user.last_name else "None",
        "tg_language": f"{user.language_code}" if user.language_code else "None",
    }
    return user_info


async def data_consent(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    context.user_data["data_consent"] = True
    context.user_data["info"] = get_user_full_tg_info(update.effective_user)
    await query.edit_message_text(CONFIRM_TEXT, parse_mode=PARSE_MODE)
    # return DATA_CONSENT_OVER


async def not_data_consent(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(NOT_CONFIRM_TEXT, parse_mode=PARSE_MODE)
    return ConversationHandler.END


data_concent_state = {
    DATA_CONSENT: [
        CallbackQueryHandler(data_consent, pattern="data_consent"),
        CallbackQueryHandler(not_data_consent, pattern="not_data_consent"),
    ]
}
