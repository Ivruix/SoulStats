from db.connection import get_connection


class UserData:
    @staticmethod
    def register_user(username, email, password_hash):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user_data (username, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING user_id
        """, (username, email, password_hash))
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return user_id

    @staticmethod
    def get_user_id(username):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_data WHERE username = %s LIMIT 1", (username,))
        user_id = cur.fetchone()
        cur.close()
        conn.close()
        return user_id[0] if user_id else None

    @staticmethod
    def get_user(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, password_hash
            FROM user_data 
            WHERE user_id = %s
        """, (user_id,))
        user_data = cur.fetchone()
        cur.close()
        conn.close()
        return user_data

    @staticmethod
    def already_in_use(email, username):
        # Проверяем, существует ли пользователь с таким email или username
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM user_data WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()
        cur.close()
        conn.close()
        return existing_user is not None
