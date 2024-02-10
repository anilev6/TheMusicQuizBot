from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler,
)

from datetime import datetime

from logs.mylogging import time_log_decorator

from utils.general_keyboard import get_keyboard, click_item_db, scroll_db
from utils.button_dialog_model import send_keyboard
from utils.helpers import victoryna_to_text

from handlers.teacher.audio.add import (
    file_drop_handler,
)
from handlers.teacher.done import done, done_command_handler, done_query_handler

from handlers.error import handle_telegram_timeout_errors


# Constants moved up as per your request
PARSE_MODE = "MarkDownV2"
EDIT_LAST_MENU_MESSAGE = "{}"
SELECT_VICTORYNA_HEADER = "Виберіть вікторину\:"
EDIT_OPTIONS_MESSAGE = "Редагувати\:"
GET_AUDIOS_MENU_MESSAGE = "Видаліть або додайте аудіо\:"

GET_DESCRIPTION_MESSAGE = "Введіть новий опис вікторини\:"
GET_TITLE_MESSAGE = "Введіть нову назву вікторини\:"

UPDATE_MESSAGE = "Вікторину оновлено\."
GET_DESCRIPTION_SUCSESS_MESSAGE = "Новий опис збережено\."
GET_TITLE_SUCSESS_MESSAGE = "Нову назву збережено\."
EDIT_DESCRIPTION_BUTTON = "Редагувати опис"
EDIT_TITLE_BUTTON = "Редагувати назву"
EDIT_AUDIOS_BUTTON = "Редагувати аудіо"
BACK_MESSAGE_BUTTON = "Назад"

DONE_BUTTON_TEXT = "Готово\\Пропустити"
BACK_BUTTON_TEXT = "Назад"


# STATEFUL CONVERSATION
# States
SELECT_VICTORYNA, EDIT_OPTIONS, GET_DESCRIPTION, GET_TITLE, GET_AUDIOS = range(5)


@handle_telegram_timeout_errors
async def edit_victorynas(update: Update, context: CallbackContext):
    keyboard = get_keyboard(context, "victoryna", "edit", display="title")
    await send_keyboard(
        update, context, keyboard, text=SELECT_VICTORYNA_HEADER, parse_mode=PARSE_MODE
    )
    return SELECT_VICTORYNA


@handle_telegram_timeout_errors
async def click_item_victoryna_edit(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith("click_item"):
        victoryna_index = int(data.split("_")[-1])
        context.user_data["current_victoryna_index"] = victoryna_index
        buttons = [
            [
                InlineKeyboardButton(
                    EDIT_DESCRIPTION_BUTTON,
                    callback_data="edit_victoryna_description",
                )
            ],
            [
                InlineKeyboardButton(
                    EDIT_TITLE_BUTTON,
                    callback_data="edit_victoryna_title",
                )
            ],
            [
                InlineKeyboardButton(
                    EDIT_AUDIOS_BUTTON,
                    callback_data="edit_victoryna_audios",
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
async def scroll_page_victoryna_edit(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await edit_victorynas(update, context)


@handle_telegram_timeout_errors
async def send_back_button(update: Update, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                BACK_MESSAGE_BUTTON,
                callback_data="done",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    victoryna_index = context.user_data["current_victoryna_index"]
    TEXT = victoryna_to_text(context, victoryna_index)
    await send_keyboard(
        update,
        context,
        text=EDIT_LAST_MENU_MESSAGE.format(TEXT),
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )


@handle_telegram_timeout_errors
async def edit_description(update: Update, context: CallbackContext):
    await send_back_button(update, context)
    await context.bot.send_message(
        update.effective_chat.id, GET_DESCRIPTION_MESSAGE, parse_mode=PARSE_MODE
    )
    return GET_DESCRIPTION


@handle_telegram_timeout_errors
async def edit_title(update: Update, context: CallbackContext):
    await send_back_button(update, context)
    await context.bot.send_message(
        update.effective_chat.id, GET_TITLE_MESSAGE, parse_mode=PARSE_MODE
    )
    return GET_TITLE


@time_log_decorator
async def save_element(update: Update, context: CallbackContext, flag):
    answer = update.message.text
    victoryna_index = context.user_data.get("current_victoryna_index")
    current_victoryna = context.user_data["victorynas"][victoryna_index]

    # edit
    current_victoryna[flag] = answer
    current_victoryna["last_edited"] = datetime.now()

    await context.bot.send_message(
        update.effective_chat.id, UPDATE_MESSAGE, parse_mode=PARSE_MODE
    )
    return await edit_victorynas(update, context)


@handle_telegram_timeout_errors
async def get_description_edit_victoryna(update: Update, context: CallbackContext):
    return await save_element(update, context, "description")


@handle_telegram_timeout_errors
async def get_title_edit_victoryna(update: Update, context: CallbackContext):
    return await save_element(update, context, "title")


# pick or unpick an audio ----------------------------------------------------------------------------
def prefill_current_list(update: Update, context: CallbackContext):
    if context.user_data.get("current_list") == None:
        victoryna_index = context.user_data.get("current_victoryna_index")
        current_victoryna = context.user_data["victorynas"][victoryna_index]
        all_audios = context.user_data["audios"]
        added_audio_indexes = [all_audios.index(a) for a in current_victoryna["audios"]]
        context.user_data["current_list"] = added_audio_indexes


@handle_telegram_timeout_errors
async def edit_audios(update: Update, context: CallbackContext):
    prefill_current_list(update, context)
    keyboard = get_keyboard(
        context, "audio", "victoryna_edit", done=True, click_emoji="✅"
    )
    await send_keyboard(
        update,
        context,
        text=GET_AUDIOS_MENU_MESSAGE,
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )
    return GET_AUDIOS


@handle_telegram_timeout_errors
async def click_item_audio_victoryna_edit(update: Update, context: CallbackContext):
    click_item_db(update, context)
    return await edit_audios(update, context)


@handle_telegram_timeout_errors
async def scroll_page_audio_victoryna_edit(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await edit_audios(update, context)


@handle_telegram_timeout_errors
async def done_audio_victoryna_edit(update: Update, context: CallbackContext):
    current_list = context.user_data.pop("current_list")

    # save
    victoryna_index = context.user_data.get("current_victoryna_index")
    current_victoryna = context.user_data["victorynas"][victoryna_index]

    audios = [context.user_data["audios"][i] for i in current_list]
    current_victoryna["audios"] = audios
    current_victoryna["last_edited"] = datetime.now()

    # await context.bot.send_message(
    #     update.effective_chat.id, UPDATE_MESSAGE, parse_mode=PARSE_MODE
    # )
    return await done(update, context)


# handler ----------------------------------------------------------------------------------------------
edit_victoryna_conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(edit_victorynas, pattern="edit_victorynas")],
    states={
        SELECT_VICTORYNA: [
            CallbackQueryHandler(
                scroll_page_victoryna_edit,
                pattern=r"previous_page_victoryna_edit|next_page_victoryna_edit",
            ),
            CallbackQueryHandler(
                click_item_victoryna_edit, pattern=r"click_item_victoryna_edit_\d+"
            ),
        ],
        EDIT_OPTIONS: [
            CallbackQueryHandler(
                edit_description,
                pattern="edit_victoryna_description",
            ),
            CallbackQueryHandler(
                edit_title,
                pattern="edit_victoryna_title",
            ),
            CallbackQueryHandler(
                edit_audios,
                pattern="edit_victoryna_audios",
            ),
        ],
        GET_DESCRIPTION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, get_description_edit_victoryna
            )
        ],
        GET_TITLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_title_edit_victoryna)
        ],
        GET_AUDIOS: [
            CallbackQueryHandler(
                scroll_page_audio_victoryna_edit,
                pattern=r"previous_page_audio_victoryna_edit|next_page_audio_victoryna_edit",
            ),
            CallbackQueryHandler(
                click_item_audio_victoryna_edit,
                pattern=r"click_item_audio_victoryna_edit_\d+",
            ),
            CallbackQueryHandler(
                done_audio_victoryna_edit, pattern="done_audio_victoryna_edit"
            ),
        ],
    },
    fallbacks=[done_query_handler, done_command_handler, file_drop_handler],
    per_message=False,
)
