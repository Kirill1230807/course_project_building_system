from django.db import connection


class ManagementQueries:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT m.id, m.name, e.last_name || ' ' || e.first_name AS head_name, m.notes
                           FROM managements m
                                    LEFT JOIN employees e ON m.head_employee_id = e.id
                           ORDER BY m.id;
                           """)
            return cursor.fetchall()

    @staticmethod
    def add(name, head_employee_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO managements (name, head_employee_id, notes)
                           VALUES (%s, %s, %s);
                           """, [name, head_employee_id or None, notes])

    @staticmethod
    def update(mid, name, head_employee_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE managements
                           SET name             = %s,
                               head_employee_id = %s,
                               notes            = %s
                           WHERE id = %s;
                           """, [name, head_employee_id or None, notes, mid])

    @staticmethod
    def delete(mid):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM managements WHERE id = %s;", [mid])


class EngineerQueries:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id, e.last_name, e.first_name, p.title AS position_title, e.salary
                           FROM employees e
                                    JOIN positions p ON e.position_id = p.id
                           WHERE e.category = 'Інженерно-технічний персонал'
                           ORDER BY e.last_name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def add(first_name, last_name, father_name, birthday, start_date, salary, position_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO employees (first_name, last_name, father_name, birthday, start_date, salary,
                                                  position_id, category)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, 'Інженерно-технічний персонал');
                           """, [first_name, last_name, father_name, birthday, start_date, salary, position_id])

    @staticmethod
    def delete(eid):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s;", [eid])
