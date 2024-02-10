from telegram import Update
from telegram.ext import CallbackContext

import asyncio
import functools

from logs.mylogging import logger, redacted
from settings.settings import ADMIN_GROUP, TEACHER_GROUP


# --------------------------------------CHECKERS--------------------------------------------
def is_user_admin(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)
    return sender_id in ADMIN_GROUP


def is_user_teacher(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)
    return sender_id in TEACHER_GROUP or sender_id in context.bot_data.get(
        "teachers", []
    )


def is_allowed_user(update: Update, context: CallbackContext):
    # bot check
    if update.effective_user.is_bot:
        return False

    # ban check
    sender_id = str(update.effective_user.id)
    return sender_id not in context.bot_data.get("banned_users", [])


# -------------------------------------DECORATOR--------------------------------------------
def check_role_decorator(allowed_role_checker_list=[is_allowed_user]):
    def general_decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args):
            try:
                for role_checker in allowed_role_checker_list:
                    if not role_checker(*args):
                        return None
                result = await func(*args)
                return result
            except Exception as e:
                message = f"Error in {func.__name__}: {redacted(str(e))}"
                logger.error(message)
                raise e

        @functools.wraps(func)
        def wrapper(*args):
            try:
                result = func(*args)
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {redacted(str(e))}")
                raise e

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return general_decorator
