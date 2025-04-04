from dotenv import load_dotenv
import os
from db.chat import Chat
from db.connection import get_connection
from ml_backend.data_types.emotion import Emotion
from ml_backend.agents.emotion_analyzer import EmotionAnalyzer
from ml_backend.agents.mood_analyzer import MoodAnalyzer
from ml_backend.agents.fact_extractor import FactExtractor
from ml_backend.agents.chatter import Chatter
from ml_backend.agents.chat_extender import ChatExtender
from yandex_cloud_ml_sdk import YCloudML

load_dotenv()


def get_sdk():
    return YCloudML(
        folder_id=os.getenv("FOLDER_ID"),
        auth=os.getenv("YANDEXGPT_API_KEY"),
    )


def get_next_question(chat, facts, last_message):
    sdk = get_sdk()
    chatter_model = sdk.models.completions("yandexgpt").configure(temperature=0.2)
    chatter = Chatter(chatter_model)
    new_message = chatter.generate_response(chat, facts, last_message)

    return new_message


def should_extend_chat(chat):
    sdk = get_sdk()
    chat_extender_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    chat_extender = ChatExtender(chat_extender_model)
    should_extend = chat_extender.should_extend(chat)
    return should_extend


def analyze_chat(chat_id, user_id):
    sdk = get_sdk()
    conn = get_connection()
    cur = conn.cursor()

    chat = Chat.get_chat_by_chat_id(chat_id)

    # Анализ настроения
    mood_analyzer_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    mood_analyzer = MoodAnalyzer(mood_analyzer_model)
    mood_value = mood_analyzer.analyze(chat)
    if mood_value is not None:
        cur.execute("INSERT INTO happiness_level (chat_id, val) VALUES (%s, %s)", (chat_id, mood_value))
        conn.commit()

    # Анализ эмоций
    emotion_analyzer_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    emotion_analyzer = EmotionAnalyzer(emotion_analyzer_model)
    emotion = emotion_analyzer.extract_emotion(chat)
    if emotion != Emotion.unknown:
        cur.execute("INSERT INTO main_emotion (chat_id, val) VALUES (%s, %s)", (chat_id, emotion.string))
        conn.commit()

    # Извлечение фактов о пользователе
    fact_extractor_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    fact_extractor = FactExtractor(fact_extractor_model)
    facts = fact_extractor.extract_facts(chat)
    for fact in facts:
        cur.execute("INSERT INTO fact (user_id, content) VALUES (%s, %s)", (user_id, fact))
        conn.commit()
