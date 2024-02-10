from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from handlers.callback_handlers import callback_handler

from utils.button_dialog_model import send_keyboard

from handlers.error import handle_telegram_timeout_errors

# from logs.mylogging import time_log_decorator

# a sub-menu

PARSE_MODE = "MarkDownV2"
TEXT = "Оберіть дію для вікторин\:"  
GET_VICTORYNAS_BUTTON = "Переглянути вікторини"
DELETE_VICTORYNAS_BUTTON = "Видалити вікторини"
EDIT_VICTORYNAS_BUTTON = "Редагувати вікторину"
START_VICTORYNAS_BUTTON = "Запустити вікторину"
BACK_BUTTON = "Назад"


@handle_telegram_timeout_errors
@callback_handler
async def my_victorynas(update: Update, context: CallbackContext):
    # clean stateful conversation first if present
    for key in list(context.user_data.keys()):
        if key.startswith("current"):
            context.user_data.pop(key)

    buttons = [
        [
            InlineKeyboardButton(
                START_VICTORYNAS_BUTTON,
                callback_data="start_victorynas",
            )
        ],
        [
            InlineKeyboardButton(
                GET_VICTORYNAS_BUTTON,
                callback_data="get_victorynas",
            )
        ],
        [
            InlineKeyboardButton(
                EDIT_VICTORYNAS_BUTTON,
                callback_data="edit_victorynas",
            )
        ],
        [
            InlineKeyboardButton(
                DELETE_VICTORYNAS_BUTTON,
                callback_data="delete_victorynas",
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
