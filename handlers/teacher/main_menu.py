from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from handlers.callback_handlers import callback_handler
from handlers.command_handlers import command_handler

from utils.button_dialog_model import send_keyboard

from handlers.role_check import check_role_decorator, is_allowed_user, is_user_teacher


PARSE_MODE = "MarkDownV2"
INSTRUCTION = "_Щоб завантажити аудіо\, відправте 1 mp3 файл в чат_👇\n_Бажаний розмір файлу \- до 4 MB_"
TEXT = INSTRUCTION
CREATE_VICTORYNA_BUTTON = "Створити вікторину"
MY_VICTORYNAS_BUTTON = "Мої вікторини"
MY_AUDIOS_BUTTON = "Мої аудіо"


@check_role_decorator(allowed_role_checker_list=[is_allowed_user, is_user_teacher])
@command_handler
@callback_handler
async def menu(update: Update, context: CallbackContext):
    # clean stateful conversation first if present
    for key in list(context.user_data.keys()):
        if key.startswith("current"):
            context.user_data.pop(key)

    buttons = [
        [
            InlineKeyboardButton(
                CREATE_VICTORYNA_BUTTON,
                callback_data="create_victoryna",
            )
        ],
        [
            InlineKeyboardButton(
                MY_VICTORYNAS_BUTTON,
                callback_data="my_victorynas",
            )
        ],
        [
            InlineKeyboardButton(
                MY_AUDIOS_BUTTON,
                callback_data="my_audios",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    return await send_keyboard(
        update, context, keyboard, text=TEXT, parse_mode=PARSE_MODE
    )
