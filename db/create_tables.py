from connection import get_connection

conn = get_connection()

with conn.cursor() as cur:
    cur.execute(open("create_tables.sql", "r").read())
    conn.commit()
