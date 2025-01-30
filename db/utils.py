import os

import psycopg2


def user_register(conn, username):
    cur = conn.cursor()

    # Добавляем юзернейм в таблицу
    cur.execute(f"INSERT INTO user_data (username) VALUES ('{username}')")
    conn.commit()
    return True


def user_login(conn, username, password):
    cur = conn.cursor()

    cur.execute("SELECT * FROM user_data WHERE username = %s LIMIT 1", (username,))
    user = cur.fetchone()
    if user is None:
        return None

    return user[1]

def get_usernames(conn):
    cur = conn.cursor()

    cur.execute("SELECT username FROM user_data")
    usernames = cur.fetchall()

    if usernames is None:
        return None

    return usernames

def get_user_id(conn, username):
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM user_data WHERE username = %s LIMIT 1", (username, ))
    id = cur.fetchone()

    if id is None:
        return None

    return id[0]

def get_user(conn, user_id):
    cur = conn.cursor()
    cur.execute("""
        SELECT * 
        FROM user_data 
        WHERE user_id = %s
    """, (user_id,))
    user_data = cur.fetchone()

    return user_data