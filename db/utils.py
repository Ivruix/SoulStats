def register_user(conn, username, email, password_hash):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO user_data (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING user_id
    """, (username, email, password_hash))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return True


def get_usernames(conn):
    cur = conn.cursor()

    cur.execute("SELECT username FROM user_data")
    usernames = cur.fetchall()

    if usernames is None:
        return None

    return usernames


def get_user_id(conn, username):
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM user_data WHERE username = %s LIMIT 1", (username,))
    id = cur.fetchone()

    if id is None:
        return None

    return id[0]


def get_user(conn, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, password_hash
        FROM user_data 
        WHERE user_id = %s
    """, (user_id,))
    user_data = cur.fetchone()
    return user_data


def user_exist(conn, email, username):
    # Проверяем, что пользователь с таким email или username не существует
    cur = conn.cursor()
    cur.execute("SELECT * FROM user_data WHERE email = %s OR username = %s", (email, username))
    existing_user = cur.fetchone()

    if existing_user:
        return True
    return False


def get_all_messages(conn, chat_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT message_id, chat_id, created_at, by_user, content 
        FROM message 
        WHERE chat_id = %s 
        ORDER BY created_at ASC
    """, (chat_id,))
    messages = cur.fetchall()
    cur.close()
    return messages


def delete_fact(conn, fact_id):
    cur = conn.cursor()
    cur.execute("DELETE FROM fact WHERE fact_id = %s", (fact_id,))
    conn.commit()
