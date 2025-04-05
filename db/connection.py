import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(f"""
        dbname=prod
        user=postgres
        password={os.getenv('DB_PASSWORD')}
    """)
