from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import asyncio
import os

from handlers.callback_handlers import callback_handler
from handlers.teacher.main_menu import menu

from utils.general_keyboard import get_keyboard, scroll_db, click_item_db
from utils.button_dialog_model import send_keyboard

from audios import defaults

from handlers.error import handle_telegram_timeout_errors


# Text Constants
SELECT_AUDIO_HEADER = "Виберіть аудіо для видалення\:"
CONFIRMATION_AUDIO_TEXT = "Ви дійсно хочете видалити *{}* аудіо файл\(и\)\?"
DELETION_AUDIO_SUCCESS_TEXT = "Аудіо файл\(и\) успішно видалені\."
PARSE_MODE = "MarkDownV2"
BACK_BUTTON_TEXT = "Ні, повернутися назад"
DELETE_AUDIO_BUTTON_TEXT = "Так, видалити"


@handle_telegram_timeout_errors
@callback_handler
async def delete_audios(update: Update, context: CallbackContext):
    keyboard = get_keyboard(
        context,
        "audio",
        "delete",
        display="description",
        back_button_callback_data="menu",
        done=True,
    )
    await send_keyboard(
        update, context, keyboard, text=SELECT_AUDIO_HEADER, parse_mode=PARSE_MODE
    )


@handle_telegram_timeout_errors
@callback_handler
async def previous_page_audio_delete(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await delete_audios(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def next_page_audio_delete(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await delete_audios(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def click_item_audio_delete(update: Update, context: CallbackContext):
    click_item_db(update, context)
    return await delete_audios(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def done_audio_delete(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    current_list = context.user_data.get("current_list")
    if current_list:
        TEXT = CONFIRMATION_AUDIO_TEXT.format(len(current_list))
        buttons = [
            [
                InlineKeyboardButton(
                    DELETE_AUDIO_BUTTON_TEXT,
                    callback_data="confirm_delete_audio",
                ),
                InlineKeyboardButton(
                    BACK_BUTTON_TEXT,
                    callback_data="delete_audios",
                ),
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        return await send_keyboard(
            update,
            context,
            keyboard,
            text=TEXT,
            parse_mode=PARSE_MODE,
        )
    return await menu(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def confirm_delete_audio(update: Update, context: CallbackContext):
    query = update.callback_query
    # await query.answer()

    current_list_indexes = context.user_data.get("current_list")
    current_list_audios = [context.user_data["audios"][i] for i in current_list_indexes]
    # delete from audios
    context.user_data["audios"] = [
        item
        for i, item in enumerate(context.user_data["audios"])
        if i not in current_list_indexes
    ]

    # delete from victorynas
    victorynas = context.user_data.get("victorynas")
    if victorynas:
        for victoryna in victorynas:
            victoryna["audios"] = [
                item for item in victoryna["audios"] if item not in current_list_audios
            ]

    # delete from the server
    for audio in current_list_audios:
        file_path = audio.get("file_path")
        if file_path not in defaults.paths:
            os.remove(file_path)

    await query.edit_message_text(
        text=DELETION_AUDIO_SUCCESS_TEXT, parse_mode=PARSE_MODE
    )

    await asyncio.sleep(3)
    return await menu(update, context)
