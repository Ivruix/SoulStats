from db.connection import get_connection


class Stats:
    @staticmethod
    def get_happiness_level(user_id):
        conn = get_connection()
        cur = conn.cursor()
        # Получаем данные из таблицы happiness_level через chat_id
        cur.execute("""
            SELECT c.created_at, hl.val
            FROM happiness_level hl
            JOIN chat c ON hl.chat_id = c.chat_id
            WHERE c.user_id = %s
            ORDER BY c.created_at ASC
        """, (user_id,))
        data = cur.fetchall()
        cur.close()

        return data
