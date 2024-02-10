from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from datetime import datetime

from utils.general_keyboard import get_keyboard, scroll_db
from utils.button_dialog_model import send_keyboard

from handlers.teacher.audio.add import file_drop_handler
from handlers.teacher.done import done_command_handler, done_query_handler

from handlers.error import handle_telegram_timeout_errors

# Constants moved up as per your request
PARSE_MODE = "MarkDownV2"
EDIT_LAST_MENU_MESSAGE = "{}"
SELECT_AUDIO_HEADER = "Виберіть аудіо\:"
EDIT_OPTIONS_MESSAGE = "Редагувати текст\?"
GET_DESCRIPTION_MESSAGE = "Введіть новий опис ayдіо\:"
UPDATE_MESSAGE = "Аудіо оновлено\."
GET_DESCRIPTION_SUCSESS_MESSAGE = "Новий опис збережено\."

EDIT_DESCRIPTION_BUTTON = "Редагувати опис"
BACK_MESSAGE_BUTTON = "Назад"

DONE_BUTTON_TEXT = "Готово\\Пропустити"
BACK_BUTTON_TEXT = "Назад"


# STATEFUL CONVERSATION
# States
SELECT_AUDIO, EDIT_OPTIONS, GET_DESCRIPTION = range(3)


@handle_telegram_timeout_errors
async def edit_audios(update: Update, context: CallbackContext):
    keyboard = get_keyboard(context, "audio", "edit")
    await send_keyboard(
        update, context, keyboard, text=SELECT_AUDIO_HEADER, parse_mode=PARSE_MODE
    )
    return SELECT_AUDIO


@handle_telegram_timeout_errors
async def click_item_audio_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith("click_item"):
        audio_index = int(data.split("_")[-1])
        context.user_data["current_audio_index"] = audio_index
        buttons = [
            [
                InlineKeyboardButton(
                    EDIT_DESCRIPTION_BUTTON,
                    callback_data="edit_description",
                )
            ],
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
            text=EDIT_OPTIONS_MESSAGE,
            keyboard=keyboard,
            parse_mode=PARSE_MODE,
        )
        return EDIT_OPTIONS


@handle_telegram_timeout_errors
async def scroll_page_audio_edit(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await edit_audios(update, context)


@handle_telegram_timeout_errors
async def edit_description(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                BACK_MESSAGE_BUTTON,
                callback_data="done",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    audio_index = context.user_data["current_audio_index"]
    await send_keyboard(
        update,
        context,
        text=EDIT_LAST_MENU_MESSAGE.format(
            context.user_data["audios"][audio_index]["description"]
        ),
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )

    await context.bot.send_message(
        update.effective_chat.id, GET_DESCRIPTION_MESSAGE, parse_mode=PARSE_MODE
    )
    return GET_DESCRIPTION


@handle_telegram_timeout_errors
async def get_description_edit_audio(update: Update, context: CallbackContext):
    answer = update.message.text
    victoryna_index = context.user_data.get("current_audio_index")
    current_audio = context.user_data["audios"][victoryna_index]
    old_description = current_audio["description"]

    # edit
    time_now = datetime.now()
    current_audio["description"] = answer
    current_audio["last_edited"] = time_now

    # edit in all the victorynas too
    victorynas = context.user_data.get("victorynas")
    if victorynas:
        for victoryna in victorynas:
            for audio in victoryna["audios"]:
                if audio["description"] == old_description:
                    audio["description"] = answer
                    audio["last_edited"] = time_now

    # TODO
    # audio file-paths-uuid are stored in a victoryna

    await context.bot.send_message(
        update.effective_chat.id, UPDATE_MESSAGE, parse_mode=PARSE_MODE
    )
    return await edit_audios(update, context)


edit_audio_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_audios, pattern="edit_audios")],
    states={
        SELECT_AUDIO: [
            CallbackQueryHandler(
                scroll_page_audio_edit,
                pattern=r"previous_page_audio_edit|next_page_audio_edit",
            ),
            CallbackQueryHandler(
                click_item_audio_edit, pattern=r"click_item_audio_edit_\d+"
            ),
        ],
        EDIT_OPTIONS: [
            CallbackQueryHandler(
                edit_description,
                pattern="edit_description",
            ),
        ],
        GET_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_description_edit_audio)
        ],
    },
    fallbacks=[done_query_handler, done_command_handler, file_drop_handler],
    per_message=False,
)
