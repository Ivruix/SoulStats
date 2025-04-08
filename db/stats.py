from db.connection import get_connection


class Stats:
    @staticmethod
    def get_happiness_by_period(user_id, period):
        conn = get_connection()
        cur = conn.cursor()

        if period == 'week':
            query = """
                SELECT c.created_at, hl.val
                FROM happiness_level hl
                JOIN chat c ON hl.chat_id = c.chat_id
                WHERE c.user_id = %s AND c.created_at >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY c.created_at ASC
            """
        elif period == 'month':
            query = """
                SELECT c.created_at, hl.val
                FROM happiness_level hl
                JOIN chat c ON hl.chat_id = c.chat_id
                WHERE c.user_id = %s AND c.created_at >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY c.created_at ASC
            """
        else:  # 'all'
            query = """
                SELECT c.created_at, hl.val
                FROM happiness_level hl
                JOIN chat c ON hl.chat_id = c.chat_id
                WHERE c.user_id = %s
                ORDER BY c.created_at ASC
            """

        cur.execute(query, (user_id,))
        data = cur.fetchall()
        cur.close()

        return data

    @staticmethod
    def get_average_happiness_by_day_of_week(user_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT TO_CHAR(c.created_at, 'Day') as day_of_week, 
                   AVG(hl.val) as avg_happiness
            FROM chat c
            JOIN happiness_level hl ON c.chat_id = hl.chat_id
            WHERE c.user_id = %s
            GROUP BY TO_CHAR(c.created_at, 'Day')
            ORDER BY CASE 
                WHEN TO_CHAR(c.created_at, 'Day') = 'Monday   ' THEN 1
                WHEN TO_CHAR(c.created_at, 'Day') = 'Tuesday  ' THEN 2
                WHEN TO_CHAR(c.created_at, 'Day') = 'Wednesday' THEN 3
                WHEN TO_CHAR(c.created_at, 'Day') = 'Thursday ' THEN 4
                WHEN TO_CHAR(c.created_at, 'Day') = 'Friday   ' THEN 5
                WHEN TO_CHAR(c.created_at, 'Day') = 'Saturday ' THEN 6
                WHEN TO_CHAR(c.created_at, 'Day') = 'Sunday   ' THEN 7
            END
        """, (user_id,))

        data = cur.fetchall()
        cur.close()

        return data

    @staticmethod
    def get_average_happiness_by_emotion(user_id):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT me.val as emotion, 
                  AVG(hl.val) as avg_happiness,
                  COUNT(*) as count
            FROM happiness_level hl
            JOIN chat c ON hl.chat_id = c.chat_id
            JOIN main_emotion me ON hl.chat_id = me.chat_id
            WHERE c.user_id = %s
            GROUP BY me.val
            ORDER BY COUNT(*) DESC
        """, (user_id,))

        data = cur.fetchall()
        cur.close()

        return data

    @staticmethod
    def get_emotions_by_period(user_id, period):
        conn = get_connection()
        cur = conn.cursor()

        if period == 'week':
            query = """
                SELECT c.created_at, me.val
                FROM main_emotion me
                JOIN chat c ON me.chat_id = c.chat_id
                WHERE c.user_id = %s AND c.created_at >= CURRENT_DATE - INTERVAL '7 days'
                ORDER BY c.created_at ASC
            """
        elif period == 'month':
            query = """
                SELECT c.created_at, me.val
                FROM main_emotion me
                JOIN chat c ON me.chat_id = c.chat_id
                WHERE c.user_id = %s AND c.created_at >= CURRENT_DATE - INTERVAL '30 days'
                ORDER BY c.created_at ASC
            """
        else:  # 'all'
            query = """
                SELECT c.created_at, me.val
                FROM main_emotion me
                JOIN chat c ON me.chat_id = c.chat_id
                WHERE c.user_id = %s
                ORDER BY c.created_at ASC
            """

        cur.execute(query, (user_id,))
        data = cur.fetchall()
        cur.close()

        return data
