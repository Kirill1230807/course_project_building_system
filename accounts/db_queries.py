from django.db import connection
from datetime import datetime

class Queries:

    @staticmethod
    def save_query(user_id, query_text, result_text: str):
        created_at = datetime.now().isoformat()

        with connection.cursor() as c:
            c.execute("""
                      INSERT INTO saved_queries (user_id, query_text, result_text, created_at)
                      VALUES (%s, %s, %s, %s)
                      """, [user_id, query_text, result_text, created_at])

    @staticmethod
    def get_saved_queries(user_id):
        with connection.cursor() as c:
            c.execute("SELECT id, user_id, query_text, result_text, created_at FROM saved_queries WHERE user_id = %s",
                      [user_id])
            rows = c.fetchall()

        return [
            {
                "id": r[0],
                "user_id": r[1],
                "query": r[2],
                "result_text": r[3],
                "created_at": r[4],
            }
            for r in rows
        ]

    @staticmethod
    def execute_sql(query):
        with connection.cursor() as c:
            c.execute(query)
            rows = c.fetchall()
            colnames = [col[0] for col in c.description]
            return {"columns": colnames, "rows": rows}