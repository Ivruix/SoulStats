
from db.chat import Chat
from db.connection import get_connection
from ml_backend.data_types.emotion import Emotion
from ml_backend.agents.emotion_analyzer import EmotionAnalyzer
from ml_backend.agents.mood_analyzer import MoodAnalyzer
from ml_backend.agents.fact_extractor import FactExtractor
from ml_backend.agents.chatter import Chatter
from ml_backend.agents.chat_extender import ChatExtender


def get_next_question(chat, facts, last_message):
    chatter = Chatter()
    new_message = chatter.generate_response(chat, facts, last_message)
    return new_message


def should_extend_chat(chat):
    chat_extender = ChatExtender()
    should_extend = chat_extender.should_extend(chat)
    return should_extend


def analyze_chat(chat_id, user_id):
    conn = get_connection()
    cur = conn.cursor()

    chat = Chat.get_chat_by_chat_id(chat_id)
    if len(chat) == 0:
        return

    # Анализ настроения
    mood_analyzer = MoodAnalyzer()
    mood_value = mood_analyzer.analyze(chat)
    if mood_value is not None:
        cur.execute("INSERT INTO happiness_level (chat_id, val) VALUES (%s, %s)", (chat_id, mood_value))
        conn.commit()

    # Анализ эмоций
    emotion_analyzer = EmotionAnalyzer()
    emotion = emotion_analyzer.extract_emotion(chat)
    if emotion != Emotion.unknown:
        cur.execute("INSERT INTO main_emotion (chat_id, val) VALUES (%s, %s)", (chat_id, emotion.string))
        conn.commit()

    # Извлечение фактов о пользователе
    fact_extractor = FactExtractor()
    facts = fact_extractor.extract_facts(chat)
    for fact in facts:
        cur.execute("INSERT INTO fact (user_id, content) VALUES (%s, %s)", (user_id, fact))
        conn.commit()
