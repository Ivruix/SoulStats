from datetime import date

from ml_backend.data_types.chat import Chat
from ml_backend.data_types.emotion import Emotion
from ml_backend.agents.emotion_analyzer import EmotionAnalyzer
from ml_backend.agents.mood_analyzer import MoodAnalyzer
from ml_backend.agents.fact_extractor import FactExtractor


def create_or_get_today_chat(conn, user_id):
    cur = conn.cursor()

    # Получаем текущую дату и дату последнего чата
    cur.execute(f"SELECT created_at FROM chat WHERE user_id = {user_id} ORDER BY created_at DESC")
    last_chat_date = cur.fetchone()
    last_chat_date = None if last_chat_date is None else last_chat_date[0]
    current_date = date.today()

    # Сравниваем, если сегодня чата еще не было, создаем
    if last_chat_date is None or last_chat_date != current_date:
        cur.execute(f"INSERT INTO chat (user_id, created_at) VALUES ({user_id}, \'{current_date.year}-{current_date.month}-{current_date.day}\')")
        conn.commit()

    # Возвращаем chat_id сегодняшнего чата
    cur.execute(f"SELECT chat_id FROM chat WHERE user_id = {user_id} ORDER BY created_at DESC")
    chat_id = cur.fetchone()[0]

    return chat_id


def get_chat_by_chat_id(conn, chat_id):
    cur = conn.cursor()

    # Получаем сообщения и конвертируем в Chat класс
    cur.execute(f"SELECT content, by_user FROM message WHERE chat_id = {chat_id} ORDER BY created_at")
    messages = cur.fetchall()
    chat = Chat.from_db_messages(messages)

    return chat


def add_assistant_message(conn, chat_id, message):
    cur = conn.cursor()

    cur.execute(f"INSERT INTO message (chat_id, by_user, content) VALUES ({chat_id}, false, \'{message}\')")
    conn.commit()


def add_user_message(conn, chat_id, message):
    cur = conn.cursor()

    cur.execute(f"INSERT INTO message (chat_id, by_user, content) VALUES ({chat_id}, true, \'{message}\')")
    conn.commit()


def analyze_chat(conn, sdk, chat_id, user_id):
    cur = conn.cursor()

    chat = get_chat_by_chat_id(conn, chat_id)

    # Анализ настроения
    mood_analyzer_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    mood_analyzer = MoodAnalyzer(mood_analyzer_model)
    mood_value = mood_analyzer.analyze(chat)
    if mood_value is not None:
        cur.execute(f"INSERT INTO happiness_level (chat_id, val) VALUES ({chat_id}, {mood_value})")
        conn.commit()

    # Анализ эмоций
    emotion_analyzer_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    emotion_analyzer = EmotionAnalyzer(emotion_analyzer_model)
    emotion = emotion_analyzer.analyze(chat)
    if emotion != Emotion.unknown:
        cur.execute(f"INSERT INTO main_emotion (chat_id, val) VALUES ({chat_id}, \'{emotion.string}\')")
        conn.commit()

    # Извлечение фактов о пользователе
    fact_extractor_model = sdk.models.completions("yandexgpt").configure(temperature=0.0)
    fact_extractor = FactExtractor(fact_extractor_model)
    facts = fact_extractor.extract(chat)
    for fact in facts:
        cur.execute(f"INSERT INTO fact (user_id, content) VALUES ({user_id}, \'{fact}\')")
        conn.commit()


def get_facts_by_user(conn, user_id):
    cur = conn.cursor()

    cur.execute(f"SELECT fact_id, content FROM fact WHERE user_id = {user_id}")
    facts = [{"fact_id": row[0], "content": row[1]} for row in cur.fetchall()]
    return facts
