from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from datetime import datetime

from utils.general_keyboard import get_keyboard, click_item_db, scroll_db
from utils.button_dialog_model import send_keyboard
from utils.helpers import append_to_front

from handlers.teacher.audio.add import file_drop_handler
from handlers.teacher.done import done, done_command_handler, done_query_handler

from handlers.error import handle_telegram_timeout_errors


# STATEFUL CONVERSATION
# States
SELECT_AUDIO, GET_TITLE, GET_DESCRIPTION = range(3)

# Constants
VICTORYNAS_LIMIT = 100

SELECT_AUDIO_HEADER = "Виберіть аудіо для вікторини\:"
GET_TITLE_MESSAGE = "Яка буде назва вікторини\?"
GET_DESCRIPTION_MESSAGE = "Детальний опис вікторини\:"
SAVE_MESSAGE = "Вікторину додано\."
BACK_MESSAGE_BUTTON = "Назад"
EDIT_LAST_MENU_MESSAGE = "\~"
PARSE_MODE = "MarkDownV2"


@handle_telegram_timeout_errors
async def create_victoryna(update: Update, context: CallbackContext):
    keyboard = get_keyboard(context, "audio", "select", done=True)
    await send_keyboard(
        update, context, keyboard, text=SELECT_AUDIO_HEADER, parse_mode=PARSE_MODE
    )
    return SELECT_AUDIO


@handle_telegram_timeout_errors
async def click_item_audio_select(update: Update, context: CallbackContext):
    click_item_db(update, context)
    return await create_victoryna(update, context)


@handle_telegram_timeout_errors
async def scroll_page_audio_select(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await create_victoryna(update, context)


@handle_telegram_timeout_errors
async def done_audio_select(update: Update, context: CallbackContext):
    context.user_data["current_victoryna"] = {}
    current_list = context.user_data.get("current_list")
    if current_list:
        audios = [context.user_data["audios"][i] for i in current_list]
        context.user_data["current_victoryna"]["audios"] = audios

        buttons = [
            [
                InlineKeyboardButton(
                    BACK_MESSAGE_BUTTON,
                    callback_data="done",
                )
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)

        await send_keyboard(
            update,
            context,
            text=EDIT_LAST_MENU_MESSAGE,
            keyboard=keyboard,
            parse_mode=PARSE_MODE,
        )
        await context.bot.send_message(
            update.effective_chat.id, GET_TITLE_MESSAGE, parse_mode=PARSE_MODE
        )
        return GET_TITLE
    return await done(update, context)


@handle_telegram_timeout_errors
async def get_title(update: Update, context: CallbackContext):
    answer = update.message.text
    context.user_data["current_victoryna"]["title"] = answer
    await update.message.reply_text(GET_DESCRIPTION_MESSAGE, parse_mode=PARSE_MODE)
    return GET_DESCRIPTION


@handle_telegram_timeout_errors
async def get_description(update: Update, context: CallbackContext):
    answer = update.message.text
    context.user_data["current_victoryna"]["description"] = answer
    return await save(update, context)


@handle_telegram_timeout_errors
async def save(update: Update, context: CallbackContext):
    if not context.user_data.get("victorynas"):
        context.user_data["victorynas"] = []

    context.user_data["current_victoryna"]["created_at"] = datetime.now()

    # TODO
    # check if there's enough space, notify if not, same for audio

    context.user_data["victorynas"] = append_to_front(
        context.user_data["current_victoryna"],
        context.user_data["victorynas"],
        limit=VICTORYNAS_LIMIT,
    )

    await update.message.reply_text(SAVE_MESSAGE, parse_mode=PARSE_MODE)
    return await done(update, context)


create_victoryna_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(create_victoryna, pattern="create_victoryna")],
    states={
        SELECT_AUDIO: [
            CallbackQueryHandler(
                scroll_page_audio_select,
                pattern=r"previous_page_audio_select|next_page_audio_select",
            ),
            CallbackQueryHandler(
                click_item_audio_select, pattern=r"click_item_audio_select_\d+"
            ),
            CallbackQueryHandler(done_audio_select, pattern="done_audio_select"),
        ],
        GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
        GET_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_description),
        ],
    },
    fallbacks=[done_query_handler, done_command_handler, file_drop_handler],
    per_message=False,
)
