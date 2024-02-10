from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from handlers.callback_handlers import callback_handler

from utils.button_dialog_model import send_keyboard

from handlers.error import handle_telegram_timeout_errors

# a sub-menu for audio management

PARSE_MODE = "MarkDownV2"
TEXT = "Оберіть дію для аудіофайлів\:"

GET_AUDIOS_BUTTON = "Переглянути аудіо"  # Button text for viewing audios
UPDATE_AUDIOS_BUTTON = "Редагувати аудіо"  # Button text for editing an audio
DELETE_AUDIOS_BUTTON = "Видалити аудіо"  # Button text for deleting audios
BACK_BUTTON = "Назад"  # Back button text


@handle_telegram_timeout_errors
@callback_handler
async def my_audios(update: Update, context: CallbackContext):
    # clean stateful conversation first if present
    for key in list(context.user_data.keys()):
        if key.startswith("current"):
            context.user_data.pop(key)

    buttons = [
        [
            InlineKeyboardButton(
                GET_AUDIOS_BUTTON,
                callback_data="get_audios",
            )
        ],
        [
            InlineKeyboardButton(
                UPDATE_AUDIOS_BUTTON,
                callback_data="edit_audios",
            )
        ],
        [
            InlineKeyboardButton(
                DELETE_AUDIOS_BUTTON,
                callback_data="delete_audios",
            )
        ],
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data="menu",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(
        update, context, keyboard, text=TEXT, parse_mode=PARSE_MODE
    )
