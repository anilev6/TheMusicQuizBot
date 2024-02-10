from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from logs.mylogging import time_log_decorator
from handlers.callback_handlers import callback_handler

from utils.general_keyboard import get_keyboard, scroll_db
from utils.button_dialog_model import send_keyboard
from utils.helpers import victoryna_to_text

from handlers.error import handle_telegram_timeout_errors

# Constants
SELECT_VICTORYNA_HEADER = "Ваші вікторини\:"
BACK_BUTTON = "Назад"
EDIT_VICTORYNA_BUTTON = "Редагувати"
SEND_AUDIOS_BUTTON_TEXT = "Послухати"
PARSE_MODE = "MarkDownV2"


@handle_telegram_timeout_errors
@callback_handler
async def get_victorynas(update: Update, context: CallbackContext):
    keyboard = get_keyboard(
        context, "victoryna", "get", display="title", back_button_callback_data="menu"
    )
    await send_keyboard(
        update, context, keyboard, text=SELECT_VICTORYNA_HEADER, parse_mode=PARSE_MODE
    )


@handle_telegram_timeout_errors
@callback_handler
async def previous_page_victoryna_get(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await get_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def next_page_victoryna_get(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await get_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def click_item_victoryna_get(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    victoryna_index = int(data.split("_")[-1])
    TEXT = f"*{victoryna_index+1}\.* " + victoryna_to_text(context, victoryna_index)
    buttons = [
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data="get_victorynas",
            )
        ],
        [
            InlineKeyboardButton(
                SEND_AUDIOS_BUTTON_TEXT,
                callback_data=f"send_audios_{victoryna_index}",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await send_keyboard(
        update,
        context,
        text=TEXT,
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )


@handle_telegram_timeout_errors
@callback_handler
async def send_audios(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    victoryna_index = int(data.split("_")[-1])

    victoryna = context.user_data["victorynas"][victoryna_index]
    message_id = 0
    for audio in victoryna.get("audios", []):
        path = audio.get("file_path")
        caption = audio.get("description")
        with open(path, "rb") as audio_file:
            sent_message = await context.bot.send_audio(
                query.message.chat_id, audio_file, caption=caption
            )
            if not context.user_data.get("current_messages"):
                context.user_data["current_messages"] = []
            context.user_data["current_messages"].append(sent_message.message_id)

    TEXT = victoryna_to_text(context, victoryna_index)
    buttons = [
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data=f"remove_audios_messages_and_return_{message_id}",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await send_keyboard(
        update,
        context,
        text=TEXT,
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )


@handle_telegram_timeout_errors
@callback_handler
async def remove_audios_messages_and_return(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    message_ids = context.user_data.get("current_messages", [])
    for m in message_ids:
        await context.bot.delete_message(query.message.chat_id, m)
    context.user_data.pop("current_messages")
    return await get_victorynas(update, context)
