from django.db import connection


class EmployeeQueries:

    # Отримати всіх працівників
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id, e.first_name, e.last_name, e.salary, p.title AS position, e.category
                           FROM employees e
                                    JOIN positions p ON e.position_id = p.id
                           WHERE e.category = 'Робітники'
                           ORDER BY e.last_name;
                           """)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Додати працівника
    @staticmethod
    def add(first_name, last_name, father_name, birthday, start_date, salary, position_id, category):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO employees (first_name, last_name, father_name, birthday, start_date, salary,
                                                  position_id, category)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                           """,
                           [first_name, last_name, father_name, birthday, start_date, salary, position_id, category])

    # Видалити працівника
    @staticmethod
    def delete(employee_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s;", [employee_id])

    @staticmethod
    def get_by_id(employee_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.first_name,
                                  e.last_name,
                                  e.father_name,
                                  e.birthday,
                                  e.start_date,
                                  e.end_date,
                                  e.salary,
                                  e.category,
                                  p.title AS position
                           FROM employees e
                                    JOIN positions p ON e.position_id = p.id
                           WHERE e.id = %s;
                           """, [employee_id])
            row = cursor.fetchone()
            if not row:
                return None
            column = [col[0] for col in cursor.description]
            return dict(zip(column, row))

    @staticmethod
    def update(employee_id, first_name, last_name, father_name, birthday, start_date, end_date, salary, position_id,
               category):
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
                               position_id = %s,
                               category    = %s
                           WHERE id = %s;
                           """,
                           [first_name, last_name, father_name, birthday, start_date, end_date, salary, position_id,
                            category, employee_id])
