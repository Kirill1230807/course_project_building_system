from django.db import connection


class BrigadeQueries:
    """Запити до таблиці бригад"""

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT b.id, b.name, e.last_name || ' ' || e.first_name AS leader_name, b.notes, b.status
                           FROM brigades b
                                    LEFT JOIN employees e ON b.leader_id = e.id
                           ORDER BY b.id;
                           """)
            rows = cursor.fetchall()
        return [
            {"id": r[0], "name": r[1], "leader_name": r[2], "notes": r[3], "status": r[4]}
            for r in rows
        ]

    @staticmethod
    def add(name, leader_id, notes, status="Неактивна"):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO brigades (name, leader_id, notes, status)
                           VALUES (%s, %s, %s, %s);
                           """, [name, leader_id, notes, status])

    @staticmethod
    def get_members(brigade_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id, e.last_name, e.first_name, e.position_id, e.category, bm.role
                           FROM brigade_members bm
                                    JOIN employees e ON bm.employee_id = e.id
                           WHERE bm.brigade_id = %s;
                           """, [brigade_id])
            rows = cursor.fetchall()
        return [
            {"id": r[0], "last_name": r[1], "first_name": r[2],
             "position_id": r[3], "category": r[4], "role": r[5]}
            for r in rows
        ]

    @staticmethod
    def add_member(brigade_id, employee_id, role):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO brigade_members (brigade_id, employee_id, role)
                           VALUES (%s, %s, %s);
                           """, [brigade_id, employee_id, role])
