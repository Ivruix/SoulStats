from yandex_cloud_ml_sdk import YCloudML
from dotenv import load_dotenv
import os

load_dotenv()


def get_sdk():
    return YCloudML(
        folder_id=os.getenv("FOLDER_ID"),
        auth=os.getenv("YANDEXGPT_API_KEY"),
    )
