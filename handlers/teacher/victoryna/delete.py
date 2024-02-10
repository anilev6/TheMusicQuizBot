from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import asyncio

from handlers.callback_handlers import callback_handler
from handlers.teacher.main_menu import menu

from utils.general_keyboard import get_keyboard, scroll_db, click_item_db
from utils.button_dialog_model import send_keyboard

from handlers.error import handle_telegram_timeout_errors


# Text Constants
SELECT_VICTORYNA_HEADER = "Виберіть вікторини для видалення\:"
CONFIRMATION_TEXT = "Ви дійсно хочете видалити *{}* пункт\(и\)\?"
DELETION_SUCCESS_TEXT = "Успішно видалено\."
PARSE_MODE = "MarkDownV2"
BACK_BUTTON_TEXT = "Ні, повернутися назад"
DELETE_BUTTON_TEXT = "Так, видалити"


@handle_telegram_timeout_errors
@callback_handler
async def delete_victorynas(update: Update, context: CallbackContext):
    keyboard = get_keyboard(
        context,
        "victoryna",
        "delete",
        display="title",
        back_button_callback_data="menu",
        done=True,
    )
    await send_keyboard(
        update, context, keyboard, text=SELECT_VICTORYNA_HEADER, parse_mode=PARSE_MODE
    )


@handle_telegram_timeout_errors
@callback_handler
async def previous_page_victoryna_delete(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await delete_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def next_page_victoryna_delete(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await delete_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def click_item_victoryna_delete(update: Update, context: CallbackContext):
    click_item_db(update, context)
    return await delete_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def done_victoryna_delete(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    current_list = context.user_data.get("current_list")
    if current_list:
        TEXT = CONFIRMATION_TEXT.format(len(current_list))
        buttons = [
            [
                InlineKeyboardButton(
                    DELETE_BUTTON_TEXT,
                    callback_data="confirm_delete_victoryna",
                ),
                InlineKeyboardButton(
                    BACK_BUTTON_TEXT,
                    callback_data="delete_victorynas",
                ),
            ],
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        return await send_keyboard(
            update,
            context,
            text=TEXT,
            keyboard=keyboard,
            parse_mode=PARSE_MODE,
        )
    return await menu(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def confirm_delete_victoryna(update: Update, context: CallbackContext):
    query = update.callback_query

    current_list = context.user_data.get("current_list")
    context.user_data["victorynas"] = [
        item
        for i, item in enumerate(context.user_data["victorynas"])
        if i not in current_list
    ]

    await query.edit_message_text(text=DELETION_SUCCESS_TEXT, parse_mode=PARSE_MODE)
    await query.answer()
    await asyncio.sleep(3)
    return await menu(update, context)
