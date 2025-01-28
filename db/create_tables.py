import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(f"""
    dbname=test
    user=postgres
    password={os.getenv('DB_PASSWORD')}
""")

with conn.cursor() as cur:
    cur.execute(open("create_tables.sql", "r").read())
    conn.commit()
