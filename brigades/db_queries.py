from django.db import connection


class BrigadeQueries:
    """Запити до таблиці бригад"""

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT b.id, b.name, e.last_name || ' ' || e.first_name AS leader, b.status, b.notes
                           FROM brigades b
                                    LEFT JOIN employees e ON b.leader_id = e.id
                           ORDER BY b.name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def add(name, leader_id, status, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO brigades (name, leader_id, status, notes)
                           VALUES (%s, %s, %s, %s);
                           """, [name, leader_id, status, notes])

    @staticmethod
    def delete(bid):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM brigades WHERE id = %s;", [bid])

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

    @staticmethod
    def get_available_workers():
        """
        Повертає працівників, які ще не входять у жодну бригаду:
        - не є бригадиром (leader_id)
        - не є членом жодної бригади (brigade_members)
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.last_name || ' ' || e.first_name ||
                                  COALESCE(' ' || e.father_name, '') AS full_name
                           FROM employees e
                           WHERE e.id NOT IN (SELECT leader_id
                                              FROM brigades
                                              WHERE leader_id IS NOT NULL
                                              UNION
                                              SELECT employee_id
                                              FROM brigade_members)
                           ORDER BY e.last_name, e.first_name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def is_employee_free(employee_id):
        """Перевіряє, чи працівник не входить до жодної бригади і не звільнений"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM employees e
                           WHERE e.id = %s
                             AND e.end_date IS NULL
                             AND e.id NOT IN (SELECT leader_id
                                              FROM brigades
                                              WHERE leader_id IS NOT NULL
                                              UNION
                                              SELECT employee_id
                                              FROM brigade_members);
                           """, [employee_id])
            return cursor.fetchone()[0] > 0