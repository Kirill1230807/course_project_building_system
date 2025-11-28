from django.db import connection

class WorkTypeQueries:
    """SQL-запити для таблиці work_types"""

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT wt.id, wt.name, u.short_name AS unit, wt.cost_per_unit
                FROM work_types wt
                LEFT JOIN units u ON wt.unit_id = u.id
                ORDER BY wt.id;
            """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(work_type_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT wt.id, wt.name, u.short_name AS unit, wt.cost_per_unit
                FROM work_types wt
                LEFT JOIN units u ON wt.unit_id = u.id
                WHERE wt.id = %s;
            """, [work_type_id])
            return cursor.fetchone()

    @staticmethod
    def add(name, unit_id, cost_per_unit):
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO work_types (name, unit_id, cost_per_unit)
                VALUES (%s, %s, %s);
            """, [name, unit_id, cost_per_unit])

    @staticmethod
    def update(work_type_id, name, unit_id, cost_per_unit):
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE work_types
                SET name = %s,
                    unit_id = %s,
                    cost_per_unit = %s
                WHERE id = %s;
            """, [name, unit_id, cost_per_unit, work_type_id])

    @staticmethod
    def delete(work_type_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM work_types WHERE id = %s;", [work_type_id])