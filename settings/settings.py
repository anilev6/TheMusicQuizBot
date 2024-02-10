import os


def get_secret_by_name(name: str):
    return os.getenv(name)

# MongoDB
MONGO_URL = get_secret_by_name("MONGO_URL")

# TG creds
TG_BOT_TOKEN = get_secret_by_name("TG_BOT_TOKEN")

MY_TG_ID = str(get_secret_by_name("MY_TG_ID"))
TEACHER1_TG_ID = str(get_secret_by_name("TEACHER1_TG_ID"))
# TEACHER2_TG_ID = str(get_secret_by_name("TEACHER2_TG_ID"))

ADMIN_GROUP = [MY_TG_ID]
TEACHER_GROUP = [
    # MY_TG_ID,
    TEACHER1_TG_ID,
    # TEACHER2_TG_ID,
]
