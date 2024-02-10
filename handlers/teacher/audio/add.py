from datetime import datetime
from uuid import uuid4
import os

from telegram import Update
from telegram.ext import (
    CallbackContext,
    MessageHandler,
    filters,
    ConversationHandler,
)

from logs.mylogging import logger, time_log_decorator
from handlers.teacher.done import done, done_command_handler, done_query_handler

from audios.encode_to_ogg import encode_to_ogg_and_replace
from utils.helpers import append_to_front

from handlers.role_check import is_user_teacher

from handlers.error import handle_telegram_timeout_errors

# removes the annoying log of the conversation handler
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

# Stateful conversation
ALLOWED_EXTENSIONS = ["mp3", "ogg"]
AUDIOS_LIMIT = 300
FILE_SIZE_LIMIT_MB = 5

# States
GET_DESCRIPTION = 1

# Messages
PARSE_MODE = "MarkDownV2"
FILE_ADDED_MESSAGE = "Аудіо додано\."
GET_DESCRIPTION_MESSAGE = "Що це за аудіо\?"
ALLOWED_EXTENSIONS_TEXT = "\, ".join(ALLOWED_EXTENSIONS)  # escape markdown
WRONG_FORMAT_MESSAGE = (
    f"Невірний формат файлу\!\nБудь ласка використовуйте {ALLOWED_EXTENSIONS_TEXT}."
)
WRONG_SIZE_MESSAGE = f"Помилка\: завеликий файл\.\nОбмеження\: {FILE_SIZE_LIMIT_MB} MB"
AUDIOS_LIMIT_MESSAGE = (
    f"Помилка\: у вас забагато файлів\.\nОбмеження\: {AUDIOS_LIMIT} штук"
)
FAILED_TO_SAVE_MESSAGE = "Помилка збереження файлу\."
ADD_AUDIO_CANCEL_MESSAGE = "Скасовано\."

# TODO input validation for the teacher everywhere


@handle_telegram_timeout_errors
async def handle_audio(update: Update, context: CallbackContext):
    if not is_user_teacher(update, context):
        return ConversationHandler.END

    try:
        # Check the extension and size
        file_extension = update.message.effective_attachment.file_name.split(".")[-1]
        file_size = update.message.effective_attachment.file_size
        if file_extension not in ALLOWED_EXTENSIONS:
            await update.message.reply_text(WRONG_FORMAT_MESSAGE, parse_mode=PARSE_MODE)
            return await done(update, context)
        if (
            file_size > FILE_SIZE_LIMIT_MB * 1000000
        ):  # in bytes is a size of an voice message
            await update.message.reply_text(WRONG_SIZE_MESSAGE, parse_mode=PARSE_MODE)
            return await done(update, context)

        # Check how much free space teacher has left
        if len(context.user_data.get("audios", [])) >= AUDIOS_LIMIT:
            await update.message.reply_text(AUDIOS_LIMIT_MESSAGE, parse_mode=PARSE_MODE)
            # TODO save and replace older
            return await done(update, context)

        # Download
        file_name = uuid4()
        file_path = f"{file_name}.{file_extension}"
        new_file = await update.message.effective_attachment.get_file()
        new_file_path = f"{file_path}"
        await new_file.download_to_drive(new_file_path)

        # Convert and check the size again
        converted_file_path = encode_to_ogg_and_replace(new_file_path)
        if os.path.getsize(converted_file_path) > FILE_SIZE_LIMIT_MB * 1000000:
            await update.message.reply_text(WRONG_SIZE_MESSAGE, parse_mode=PARSE_MODE)
            return await done(update, context)

        # Save and continue
        context.user_data["current_audio"] = {
            "file_path": converted_file_path,
            "created_at": datetime.now(),
        }

        await update.message.reply_text(GET_DESCRIPTION_MESSAGE, parse_mode=PARSE_MODE)
        return GET_DESCRIPTION

    except Exception as e:
        logger.error(f"Error saving file: {e}")
        await update.message.reply_text(FAILED_TO_SAVE_MESSAGE, parse_mode=PARSE_MODE)
        return await done(update, context)


@handle_telegram_timeout_errors
async def get_description(update: Update, context: CallbackContext):
    answer = update.message.text
    context.user_data["current_audio"]["description"] = answer

    audios = context.user_data.get("audios")
    if not audios:
        context.user_data["audios"] = []

    context.user_data["audios"] = append_to_front(
        context.user_data["current_audio"],
        context.user_data["audios"],
        limit=AUDIOS_LIMIT,
    )

    await update.message.reply_text(FILE_ADDED_MESSAGE, parse_mode=PARSE_MODE)
    return await done(update, context)


file_drop_handler = MessageHandler(filters.AUDIO, handle_audio)

add_audio_conv_handler = ConversationHandler(
    entry_points=[file_drop_handler],
    states={
        GET_DESCRIPTION: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)
        ],
    },
    fallbacks=[done_query_handler, done_command_handler],
)
