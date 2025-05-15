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

        if '$unsub_' in email:
            return False

        cur.execute("SELECT * FROM user_data WHERE email = %s OR username = %s", (email, username))
        existing_user = cur.fetchone()
        cur.close()
        conn.close()
        return existing_user is not None

    @staticmethod
    def get_all_users():
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT user_id, username, email
            FROM user_data
        """)
        users = cur.fetchall()
        cur.close()
        conn.close()
        return users

    @staticmethod
    def get_user_by_email(email):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id, username FROM user_data WHERE email = %s LIMIT 1", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user

    @staticmethod
    def get_email_by_user_id(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT email FROM user_data WHERE user_id = %s", (user_id,))
        email = cur.fetchone()
        cur.close()
        conn.close()
        return email[0] if email else None

    @staticmethod
    def update_password(user_id, new_password_hash):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_data SET password_hash = %s WHERE user_id = %s", (new_password_hash, user_id))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def unsubscribe_user(email):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_data SET email = %s WHERE email = %s", ('$unsub_' + email, email))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def update_email(user_id, new_email):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user_data SET email = %s WHERE user_id = %s", (new_email, user_id))
        conn.commit()
        cur.close()
        conn.close()
