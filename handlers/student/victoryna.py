from telegram import Update
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
import asyncio
from datetime import datetime
from random import shuffle, randint

from logs.mylogging import logger, time_log_decorator

from handlers.data_consent_model import get_data_consent, data_consent, not_data_consent
from handlers.student.registration import reg_start_student, registration_states_student

from handlers.role_check import is_user_teacher, is_allowed_user, check_role_decorator
from handlers.teacher.main_menu import menu

from utils.helpers import victoryna_student_results_to_text
from utils.helpers import join_dictionaries, escape_markdown_v2

from audios import defaults
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which


# States
DATA_CONSENT = 0
VICTORYNA = 5  # before there's registration # TODO bring out states

# Constants
PARSE_MODE = "MarkdownV2"
READY_MESSAGE = "*Готові\?* 3\.\.\."
COUNTDOWN_MESSAGE_2 = "2..."
COUNTDOWN_MESSAGE_1 = "1..."
GOOD_LUCK_MESSAGE = "*Удачі\!* \n\n_будь ласка, відповідайте одним повідомленням_"
VICTORYNA_DONE_MESSAGE = "Ваша вікторина завершена\! \nВідпочивайте \:\)"
VICTORYNA_NOT_SET_MESSAGE = "Вікторина ще не готова\. \nВідпочивайте \:\)"
VICTORYNA_CANCELLED_MESSAGE = "Вікторину скасовано\."
WELL_DONE_MESSAGE = "Дякую\!"
TEACHER_FINISED_MESSAGE = "Нажаль, вікторину було уже завершено\."
RESULTS_MESSAGE_PREFIX = "Ваші результати\:\n\n*{}*\n\n"
START_REMINDER = "\n\nДля наступної вікторини  /start \:\)"


# helpers
@time_log_decorator
async def send_padded_voice(bot, chat_id, input_file_path, protect_content=True):
    """Anti-cheat looking at the audio duration, sometimes the size too"""
    # Old version that preserved th size and the duration
    # with open(path, "rb") as audio_file:
    #     sent_message = await context.bot.send_audio(query.message.chat_id, audio_file)
    #     message_id = sent_message.message_id  # get message id

    # Load the original audio file
    AudioSegment.converter = which("ffmpeg")
    audio = AudioSegment.from_file(input_file_path)

    # Generate a random length of silence
    silence_length = randint(
        27000, 90000
    )  # Random silence between 27 sec and 1.5 minutes
    silence = AudioSegment.silent(duration=silence_length)

    # Append silence to the original audio
    padded_audio = audio + silence

    # Use an in-memory bytes buffer for the new audio file
    buffer = BytesIO()
    padded_audio.export(buffer, format="ogg", codec="libopus")
    buffer.seek(0)  # Reset buffer to the beginning so it can be read from the start

    # Send the audio file as a voice message
    message = await bot.send_voice(
        chat_id=chat_id,
        voice=buffer,
        protect_content=protect_content,
        # message = await bot.send_audio(
        #     chat_id=chat_id, audio=buffer, protect_content=protect_content # timeout - ? TODO
    )

    message_id = message.message_id
    buffer.close()
    return message_id


def get_random_music(context: CallbackContext):
    l = list(context.bot_data["victoryna_now"]["audios"])
    shuffle(l)
    return l


def fill_defaults_teacher(context: CallbackContext):
    context.user_data["audios"] = list(defaults.audios)
    context.user_data["victorynas"] = list(defaults.victorynas)


async def consent_confirm(update: Update, context: CallbackContext):
    await data_consent(update, context)
    if is_user_teacher(update, context):
        fill_defaults_teacher(context)
        await menu(update, context)
        return ConversationHandler.END
    else:
        return await reg_start_student(update, context)


# handlers
@check_role_decorator(allowed_role_checker_list=[is_allowed_user])
async def start_student_victoryna(update: Update, context: CallbackContext):
    if not context.user_data.get("data_consent"):  # first time a user starts
        return await get_data_consent(update, context)

    if not context.bot_data.get("victoryna_now"):
        await update.message.reply_text(
            VICTORYNA_NOT_SET_MESSAGE, parse_mode=PARSE_MODE
        )
        return ConversationHandler.END

    if str(update.effective_user.id) in context.bot_data.get("victoryna_now", {}).get(
        "student_results", {}
    ):
        await update.message.reply_text(VICTORYNA_DONE_MESSAGE, parse_mode=PARSE_MODE)
        return ConversationHandler.END

    context.user_data["music"] = get_random_music(context)
    first_track = context.user_data["music"].pop()
    first_track_name = first_track["description"]
    first_track_file_path = first_track["file_path"]

    await update.message.reply_text(READY_MESSAGE, parse_mode=PARSE_MODE)
    await asyncio.sleep(1)
    await update.message.reply_text(COUNTDOWN_MESSAGE_2)
    await asyncio.sleep(1)
    await update.message.reply_text(COUNTDOWN_MESSAGE_1)
    await asyncio.sleep(1)
    await update.message.reply_text(GOOD_LUCK_MESSAGE, parse_mode=PARSE_MODE)

    # with open(first_track_file_path, "rb") as audio_file:
    #     await update.message.reply_voice(audio_file, protect_content=True)
    await send_padded_voice(
        context.bot, update.effective_user.id, first_track_file_path
    )

    context.user_data["results"] = {}
    context.user_data["current_question"] = first_track_name
    context.user_data["logs"] = [
        {"time": datetime.now(), "role": "bot", "message": first_track_name}
    ]
    logger.info(f"user {update.effective_user.id} got {first_track_name}")

    return VICTORYNA


@time_log_decorator
async def record_answer(update: Update, context: CallbackContext):
    answer = update.message.text
    context.user_data["results"][context.user_data["current_question"]] = answer
    context.user_data["logs"].append(
        {"time": datetime.now(), "role": "user", "message": answer}
    )
    logger.info(f"user {update.effective_user.id} answers {answer}")

    return await send_next_audio(update, context)


@time_log_decorator
async def send_next_audio(update: Update, context: CallbackContext):
    if not context.user_data["music"]:
        context.user_data.pop("music")
        return await victoryna_over(update, context)

    next_track = context.user_data["music"].pop()
    next_track_file_path = next_track["file_path"]
    next_track_name = next_track["description"]
    context.user_data["current_question"] = next_track_name

    # with open(next_track_file_path, "rb") as audio_file:
    #     await update.message.reply_voice(audio_file, protect_content=True)
    await send_padded_voice(context.bot, update.effective_user.id, next_track_file_path)

    context.user_data["logs"].append(
        {"time": datetime.now(), "role": "bot", "message": next_track_name}
    )
    logger.info(f"user {update.effective_user.id} got {next_track_name}")


@time_log_decorator
async def victoryna_over(update: Update, context: CallbackContext):
    victoryna = context.bot_data.get("victoryna_now")
    if not victoryna:
        await update.message.reply_text(TEACHER_FINISED_MESSAGE, parse_mode=PARSE_MODE)
        return ConversationHandler.END

    title = escape_markdown_v2(victoryna.get("title", ""))
    await update.message.reply_text(WELL_DONE_MESSAGE, parse_mode=PARSE_MODE)
    await update.message.reply_text(
        RESULTS_MESSAGE_PREFIX.format(title)
        + victoryna_student_results_to_text(context.user_data["results"])
        + START_REMINDER,
        parse_mode=PARSE_MODE,
    )

    context.user_data["logs"].append(
        {"time": datetime.now(), "role": "info", "message": "finished"}
    )
    logger.info(f"user {update.effective_user.id} has finished!")

    await save_results_for_user(update, context)
    await save_logs_for_user(update, context)
    return ConversationHandler.END


@time_log_decorator
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(VICTORYNA_CANCELLED_MESSAGE, parse_mode=PARSE_MODE)
    context.user_data["logs"].append(
        {"time": datetime.now(), "role": "info", "message": "canceled"}
    )
    logger.info(f"user {update.effective_user.id} has canceled the Victoryna!")

    await save_results_for_user(update, context)
    await save_logs_for_user(update, context)
    return ConversationHandler.END


@time_log_decorator
async def save_results_for_user(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if "results" in context.user_data:
        results = context.user_data.pop("results", {})
        context.bot_data["victoryna_now"]["student_results"][user_id] = results
        logger.info(f"user {update.effective_user.id} results: {results}")


@time_log_decorator
async def save_logs_for_user(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if "logs" in context.user_data:
        logs = context.user_data.pop("logs", [])
        context.bot_data["victoryna_now"]["student_logs"][user_id] = logs
        logger.info(f"user {update.effective_user.id} logs: {logs}")


student_victoryna_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_student_victoryna)],
    states=join_dictionaries(
        {
            DATA_CONSENT: [
                CallbackQueryHandler(consent_confirm, pattern="data_consent")
            ],
            VICTORYNA: [MessageHandler(filters.TEXT & ~filters.COMMAND, record_answer)],
        },
        registration_states_student,
    ),
    fallbacks=[
        CommandHandler("cancel", cancel),
        CallbackQueryHandler(not_data_consent, pattern="not_data_consent"),
    ],
)
