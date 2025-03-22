from db.connection import get_connection


class Fact:
    @staticmethod
    def get_facts_by_user(user_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT fact_id, content FROM fact WHERE user_id = %s", (user_id,))
        facts = [{"fact_id": row[0], "content": row[1]} for row in cur.fetchall()]
        cur.close()
        conn.close()
        return facts

    @staticmethod
    def delete_fact(fact_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM fact WHERE fact_id = %s", (fact_id,))
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def get_user_id_by_fact_id(fact_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM fact WHERE fact_id = %s", (fact_id,))
        fact_user_id = cur.fetchone()
        cur.close()
        conn.close()
        return fact_user_id[0] if fact_user_id else None

    @staticmethod
    def create_fact(user_id, content):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO fact (user_id, content) VALUES (%s, %s) RETURNING fact_id", (user_id, content))
        fact_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return fact_id

    @staticmethod
    def update_fact(fact_id, content):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("UPDATE fact SET content = %s WHERE fact_id = %s", (content, fact_id))
        conn.commit()
        cur.close()
        conn.close()
