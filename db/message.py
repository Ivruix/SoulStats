from db.connection import get_connection


class Message:
    @staticmethod
    def add_assistant_message(chat_id, message):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO message (chat_id, by_user, content) VALUES (%s, %s, %s)", (chat_id, False, message))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def add_user_message(chat_id, message):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO message (chat_id, by_user, content) VALUES (%s, %s, %s)", (chat_id, True, message))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_all_messages(chat_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT message_id, chat_id, created_at, by_user, content 
            FROM message 
            WHERE chat_id = %s 
            ORDER BY created_at ASC
        """, (chat_id,))
        messages = cur.fetchall()
        cur.close()
        conn.close()
        return messages
