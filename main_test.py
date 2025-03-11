from __future__ import annotations
from dotenv import load_dotenv
from ml_backend.agents.chatter import Chatter
from yandex_cloud_ml_sdk import YCloudML
import psycopg2
import os
from ml_backend.db.utils import *

PAID_GPT_MESSAGES = 3
MAX_CHAT_LEN = PAID_GPT_MESSAGES * 2 + 1


def have_a_chat(conn, sdk, user_id):
    chat_id = create_or_get_today_chat(conn, user_id)

    chat = get_chat_by_chat_id(conn, chat_id)
    print(chat.as_string())

    if len(chat) == MAX_CHAT_LEN:
        return

    chatter_model = sdk.models.completions("yandexgpt").configure(temperature=0.2)
    chatter = Chatter(chatter_model)
    new_message = chatter.generate_response(chat, (MAX_CHAT_LEN - len(chat) + 1) // 2)
    print(new_message)

    add_assistant_message(conn, chat_id, new_message)

    if len(chat) + 1 == MAX_CHAT_LEN:
        analyze_chat(conn, sdk, chat_id, user_id)
        return

    user_response = input()

    add_user_message(conn, chat_id, user_response)


load_dotenv()

gpt_sdk = YCloudML(
    folder_id=os.getenv("FOLDER_ID"),
    auth=os.getenv("YANDEXGPT_API_KEY"),
)

connection = psycopg2.connect(f"""
    dbname=test
    user=postgres
    password={os.getenv('DB_PASSWORD')}
""")

have_a_chat(connection, gpt_sdk, 1)
