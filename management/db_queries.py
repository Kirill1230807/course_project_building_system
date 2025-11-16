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

    @staticmethod
    def get_by_id(mid):
        """Отримати управління за ID"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, head_employee_id, notes
                           FROM managements
                           WHERE id = %s;
                           """, [mid])
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "head_employee_id": row[2],
            "notes": row[3]
        }


class EngineerQueries:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.last_name,
                                  e.first_name,
                                  p.title AS position_title,
                                  e.salary,
                                  e.end_date
                           FROM employees e
                                    JOIN positions p ON e.position_id = p.id
                           WHERE e.category = 'Інженерно-технічний персонал'
                           ORDER BY e.last_name;
                           """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

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

    @staticmethod
    def get_by_id(eid):
        """Отримати інженера за ID"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id,
                                  first_name,
                                  last_name,
                                  father_name,
                                  birthday,
                                  start_date,
                                  end_date,
                                  salary,
                                  position_id
                           FROM employees
                           WHERE id = %s;
                           """, [eid])
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "father_name": row[3],
            "birthday": row[4],
            "start_date": row[5],
            "end_date": row[6],
            "salary": row[7],
            "position_id": row[8]
        }

    @staticmethod
    def update(eid, first_name, last_name, father_name, birthday, start_date, end_date, salary, position_id):
        """Оновити дані інженера"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE employees
                           SET first_name  = %s,
                               last_name   = %s,
                               father_name = %s,
                               birthday    = %s,
                               start_date  = %s,
                               end_date    = %s,
                               salary      = %s,
                               position_id = %s
                           WHERE id = %s;
                           """,
                           [first_name, last_name, father_name, birthday, start_date, end_date, salary, position_id,
                            eid])
