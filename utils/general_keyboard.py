from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
import math


# My Framework

# 'current_' is a reserved prefix used by processes
# only one process can happen at a time
# you will have current_list available in user_data for the further manipulation
# returning to menu clears all the 'current_' from the user_data


DONE_BUTTON_TEXT = "Готово"
BACK_BUTTON_TEXT = "Назад"


def click_item_db(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith("click_item"):
        item_index = int(data.split("_")[-1])

        if not context.user_data.get("current_list"):
            context.user_data["current_list"] = []

        if item_index in context.user_data["current_list"]:
            context.user_data["current_list"].remove(item_index)

        elif item_index not in context.user_data["current_list"]:
            context.user_data["current_list"].append(item_index)


def get_state_emoji(item_index, flag, context, emoji=""):
    if not emoji:
        FLAG_TO_EMOJI = {"delete": "❌", "select": "✅"}
        emoji = FLAG_TO_EMOJI.get(flag, "✅")

    emoji = emoji if item_index in context.user_data.get("current_list", []) else ""
    return emoji


def scroll_db(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if "_page" in data:
        if not context.user_data.get("current_page"):
            context.user_data["current_page"] = 0

        if data.startswith("previous_page"):
            context.user_data["current_page"] -= 1

        if data.startswith("next_page"):
            context.user_data["current_page"] += 1


def get_keyboard(
    context: CallbackContext,
    header_flag,
    flag,
    per_page=5,
    display="description",
    click_emoji="",
    done=False,
    back_button_callback_data="done",  # 'menu' for callback handler, 'done' for finishing conversations
):

    my_entire_list = context.user_data[f"{header_flag}s"]
    max_page = math.ceil(len(my_entire_list) / per_page) - 1  # pages start with 0

    page = context.user_data.get("current_page", 0)
    start = page * per_page
    end = start + per_page
    small_list = my_entire_list[start:end]

    # necessarily create these callback functions that are callbacks
    buttons = [
        [
            InlineKeyboardButton(
                f"{get_state_emoji(item_index + start, flag, context, emoji=click_emoji)} {item_index + start + 1}. {small_list[item_index].get(display,'None')}",
                callback_data=f"click_item_{header_flag}_{flag}_{item_index + start}",
            )
        ]
        for item_index in range(len(small_list))
    ]

    # Pagination buttons
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                "◀️", callback_data=f"previous_page_{header_flag}_{flag}"
            )
        )

    if page < max_page:
        navigation_buttons.append(
            InlineKeyboardButton("▶️", callback_data=f"next_page_{header_flag}_{flag}")
        )

    # Add navigation buttons as a separate row in the keyboard
    if navigation_buttons:
        buttons.append(navigation_buttons)

    other_buttons = []
    other_buttons.append(
        InlineKeyboardButton(
            BACK_BUTTON_TEXT,
            callback_data=back_button_callback_data,
        )
    )
    if done:

        other_buttons.append(
            InlineKeyboardButton(
                DONE_BUTTON_TEXT, callback_data=f"done_{header_flag}_{flag}"
            )
        )

    buttons.append(other_buttons)

    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard
