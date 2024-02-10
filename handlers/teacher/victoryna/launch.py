from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from datetime import datetime

from logs.mylogging import time_log_decorator
from handlers.teacher.main_menu import menu
from handlers.callback_handlers import callback_handler
from handlers.error import handle_telegram_timeout_errors

from utils.general_keyboard import get_keyboard, scroll_db
from utils.button_dialog_model import send_keyboard
from utils.helpers import victoryna_to_text, append_to_front
from utils.parse_data_for_teacher import (
    victoryna_to_dataframe,
    student_results_to_dataframe,
    student_logs_to_dataframe,
    get_student_dataframe,
    save_dataframes_to_excel,
)

from settings.app import application

# TODO input validation

# Constants
PARSE_MODE = "MarkDownV2"
SELECT_VICTORYNA_HEADER = "Ваші вікторини\:"
CONFIRM_TEXT = "Розпочати цю вікторину\?\n"
VICTORYNA_ON_TEXT = "Вікторина активна\.\.\.\n*{}*"
END_BUTTON = "Закінчити"
BACK_BUTTON = "Назад"
CONFIRM_BUTTON_TEXT = "Розпочати"
MUTE_TEXT = "🎶"


@handle_telegram_timeout_errors
@callback_handler
async def start_victorynas(update: Update, context: CallbackContext):
    keyboard = get_keyboard(
        context, "victoryna", "start", display="title", back_button_callback_data="menu"
    )
    await send_keyboard(
        update, context, keyboard, text=SELECT_VICTORYNA_HEADER, parse_mode=PARSE_MODE
    )


@handle_telegram_timeout_errors
@callback_handler
async def previous_page_victoryna_start(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await start_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def next_page_victoryna_start(update: Update, context: CallbackContext):
    scroll_db(update, context)
    return await start_victorynas(update, context)


@handle_telegram_timeout_errors
@callback_handler
async def click_item_victoryna_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    data = query.data
    victoryna_index = int(data.split("_")[-1])
    TEXT = f"*{CONFIRM_TEXT}*\n" + f"{victoryna_to_text(context, victoryna_index)}"
    buttons = [
        [
            InlineKeyboardButton(
                CONFIRM_BUTTON_TEXT,
                callback_data=f"confirm_victoryna_start_{victoryna_index}",
            )
        ],
        [
            InlineKeyboardButton(
                BACK_BUTTON,
                callback_data="start_victorynas",
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
async def confirm_victoryna_start(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # check if it's possile; quit if not
    if context.bot_data.get("victoryna_now"):
        # TODO handle two or more teachers
        return await menu(update, context)

    data = query.data
    victoryna_index = int(data.split("_")[-1])
    my_victoryna = context.user_data["victorynas"][victoryna_index]

    # fill the bot data with victoryna
    context.bot_data["victoryna_now"] = {}
    context.bot_data["victoryna_now"]["started_at"] = datetime.now()
    context.bot_data["victoryna_now"]["title"] = my_victoryna["title"]
    context.bot_data["victoryna_now"]["description"] = my_victoryna["description"]
    context.bot_data["victoryna_now"]["audios"] = my_victoryna["audios"]
    context.bot_data["victoryna_now"]["student_results"] = {}
    context.bot_data["victoryna_now"]["student_logs"] = {}

    buttons = [
        [
            InlineKeyboardButton(
                END_BUTTON,
                callback_data=f"end_victorynas",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await send_keyboard(
        update,
        context,
        text=VICTORYNA_ON_TEXT.format(my_victoryna['title']),
        keyboard=keyboard,
        parse_mode=PARSE_MODE,
    )


@handle_telegram_timeout_errors
@callback_handler
async def end_victorynas(update: Update, context: CallbackContext):
    context.bot_data["victoryna_now"]["ended_at"] = datetime.now()
    victoryna = context.bot_data.pop("victoryna_now")
    # clean grab the data
    victoryna.pop("audios")

    results_archive = context.bot_data.get("results_archive",{})
    if not results_archive:
        context.bot_data["results_archive"] = {}

    teacher_id = str(update.effective_user.id)
    if not results_archive.get(teacher_id):
        context.bot_data["results_archive"][teacher_id]=[]

    context.bot_data["results_archive"][teacher_id] = append_to_front(
        victoryna, context.bot_data["results_archive"][teacher_id], limit=500
    )
    await send_victoryna_results(update, context, victoryna)
    return await menu(update, context)


@time_log_decorator
async def send_victoryna_results(update: Update, context: CallbackContext, victoryna):

    student_results = victoryna.pop("student_results")
    if student_results:
        results_table = student_results_to_dataframe(student_results)

        allowed_students = set(results_table.index)
        student_table = get_student_dataframe(application.user_data, allowed_students)

        student_logs = victoryna.pop("student_logs")
        if student_logs:
            logs_table = student_logs_to_dataframe(student_logs)

        victoryna_table = victoryna_to_dataframe(victoryna, str(update.effective_user.id))
        file = save_dataframes_to_excel(results_table, student_table, logs_table, victoryna_table)
        filename = "victoryna_results.xlsx"
        await context.bot.send_document(chat_id=update.effective_user.id, document=file, filename=filename)
