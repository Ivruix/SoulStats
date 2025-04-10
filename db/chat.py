from datetime import date
from db.connection import get_connection
from ml_backend.data_types.agent_chat import AgentChat


class Chat:
    @staticmethod
    def create_or_get_today_chat(user_id):
        conn = get_connection()
        cur = conn.cursor()
        current_date = date.today()

        cur.execute("SELECT created_at FROM chat WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        last_chat_date = cur.fetchone()
        last_chat_date = None if last_chat_date is None else last_chat_date[0]

        # Сравниваем, если сегодня чата еще не было, создаем
        if last_chat_date is None or last_chat_date != current_date:
            cur.execute("INSERT INTO chat (user_id, created_at, has_ended) VALUES (%s, %s, False)", (user_id, current_date))
            conn.commit()

        cur.execute("SELECT chat_id FROM chat WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        chat_id = cur.fetchone()[0]
        cur.close()
        conn.close()
        return chat_id

    @staticmethod
    def get_chat_by_chat_id(chat_id):
        conn = get_connection()
        cur = conn.cursor()

        # Получаем сообщения и конвертируем в AgentChat класс
        cur.execute("SELECT content, by_user FROM message WHERE chat_id = %s ORDER BY created_at", (chat_id,))
        messages = cur.fetchall()
        chat = AgentChat.from_db_messages(messages)
        cur.close()
        conn.close()
        return chat

    @staticmethod
    def get_chats_by_user(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT chat_id, created_at FROM chat WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        chats = cur.fetchall()
        cur.close()
        conn.close()
        return chats

    @staticmethod
    def has_ended(chat_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT has_ended FROM chat WHERE chat_id = %s", (chat_id,))
        ended = cur.fetchone()[0]
        cur.close()
        conn.close()
        return ended

    @staticmethod
    def mark_chat_as_ended(chat_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE chat SET has_ended = TRUE WHERE chat_id = %s", (chat_id,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_active_chats():
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT chat_id, user_id, created_at FROM chat WHERE has_ended = FALSE")
        active_chats = cur.fetchall()

        cur.close()
        conn.close()
        return active_chats

    @staticmethod
    def get_latest_chat(user_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT chat_id, created_at
            FROM chat
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        result = cur.fetchone()

        cur.close()
        conn.close()
        return result

