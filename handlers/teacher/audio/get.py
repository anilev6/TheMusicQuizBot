from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from handlers.callback_handlers import callback_handler

from utils.general_keyboard import get_keyboard, scroll_db
from utils.button_dialog_model import send_keyboard
from utils.helpers import escape_markdown_v2

from handlers.error import handle_telegram_timeout_errors


# Constants
SELECT_AUDIO_HEADER = "Ваші аудіофайли\:"
BACK_BUTTON = "Назад"
SEND_AUDIO_BUTTON = "Послухати"
EDIT_AUDIO_BUTTON = "Редагувати"
PARSE_MODE = "MarkDownV2"


@handle_telegram_timeout_errors
@callback_handler
async def get_audios(update: Update, context: CallbackContext):
    keyboard = get_keyboard(
        context,
        "audio",
        "get",
        display="description",
        back_button_callback_data="menu",
    )
    await send_keyboard(
        update,
        context,
        keyboard,
        text=SELECT_AUDIO_HEADER,
        parse_mode=PARSE_MODE,
    )


@handle_telegram_timeout_errors
@callback_handler
async def previous_page_audio_get(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await get_audios(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def next_page_audio_get(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await get_audios(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def click_item_audio_get(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    audio_index = int(data.split("_")[-1])
    TEXT = f"{audio_index+1}\. " + escape_markdown_v2(
        context.user_data.get("audios")[audio_index]["description"]
    )
    buttons = [
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data="get_audios",
            )
        ],
        [
            InlineKeyboardButton(
                SEND_AUDIO_BUTTON,
                callback_data=f"send_audio_{audio_index}",
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
async def send_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    audio_index = int(data.split("_")[-1])
    audio = context.user_data["audios"][audio_index]
    message_id = 0

    path = audio.get("file_path")
    with open(path, "rb") as audio_file:
        sent_message = await context.bot.send_audio(query.message.chat_id, audio_file)
        message_id = sent_message.message_id

    TEXT = (
        f"*{audio_index+1}\.* "
        + f'*{escape_markdown_v2(context.user_data.get("audios")[audio_index]["description"])}*'
    )
    buttons = [
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data=f"remove_audio_message_and_return_{message_id}",
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
async def remove_audio_message_and_return(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    message_id = int(data.split("_")[-1])
    await context.bot.delete_message(query.message.chat_id, message_id)
    return await get_audios(update, context)
