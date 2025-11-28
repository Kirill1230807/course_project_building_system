from django.db import connection


class EquipmentQueries:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.name,
                                  t.title AS type_title,
                                  e.status,
                                  s.name  AS site_name,
                                  e.notes
                           FROM equipment e
                                    LEFT JOIN equipment_types t ON e.type_id = t.id
                                    LEFT JOIN construction_sites s ON e.assigned_site_id = s.id
                           ORDER BY e.id;
                           """)
            return cursor.fetchall()

    @staticmethod
    def add(name, type_id, status, assigned_site_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO equipment (name, type_id, status, assigned_site_id, notes)
                           VALUES (%s, %s, %s, %s, %s);
                           """, [name, type_id, status, assigned_site_id, notes])

    @staticmethod
    def delete(equipment_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM equipment WHERE id = %s;", [equipment_id])

    @staticmethod
    def get_by_id(equipment_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, type_id, status, assigned_site_id, notes
                           FROM equipment
                           WHERE id = %s;
                           """, [equipment_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "type_id": row[2],
            "status": row[3],
            "assigned_site_id": row[4],
            "notes": row[5]
        }

    @staticmethod
    def update(equipment_id, name, type_id, status, assigned_site_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE equipment
                           SET name             = %s,
                               type_id          = %s,
                               status           = %s,
                               assigned_site_id = %s,
                               notes            = %s
                           WHERE id = %s;
                           """, [name, type_id, status, assigned_site_id, notes, equipment_id])

    @staticmethod
    def update_status_based_on_site():
        """Приводимо статуси до базових, але НЕ чіпаємо 'В ремонті'."""
        with connection.cursor() as c:
            c.execute("""
                      UPDATE equipment
                      SET status = 'Вільна'
                      WHERE assigned_site_id IS NULL
                        AND status <> 'В ремонті';
                      """)
            c.execute("""
                      UPDATE equipment
                      SET status = 'В роботі'
                      WHERE assigned_site_id IS NOT NULL
                        AND status <> 'В ремонті';
                      """)

    @staticmethod
    def get_types():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title FROM equipment_types ORDER BY title;")
            rows = cursor.fetchall()
            return [{"id": r[0], "title": r[1]} for r in rows]

    @staticmethod
    def add_types(name, type_id, status, assigned_site_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO equipment (name, type_id, status, assigned_site_id, notes)
                           VALUES (%s, %s, %s, %s, %s);
                           """, [name, type_id, status, assigned_site_id, notes])

    @staticmethod
    def unassign_equipment_from_finished_site(site_id):
        """Відкріплює всю техніку від завершеного об'єкта та робить її 'Вільна'"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE equipment
                           SET assigned_site_id = NULL,
                               status           = CASE
                                                      WHEN status != 'В ремонті' THEN 'Вільна'
                                                      ELSE status
                                   END
                           WHERE assigned_site_id = %s;
                           """, [site_id])

    @staticmethod
    def close_active_history(equipment_id):
        """
        Закриває активний запис історії для техніки.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE equipment_work_history
                           SET end_date = CURRENT_DATE
                           WHERE equipment_id = %s
                             AND end_date IS NULL;
                           """, [equipment_id])

    @staticmethod
    def add_history_entry(equipment_id, site_id, notes=None):
        """
        Створює новий запис — техніку призначено на об’єкт.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO equipment_work_history (equipment_id, site_id, start_date, notes)
                           VALUES (%s, %s, CURRENT_DATE, %s);
                           """, [equipment_id, site_id, notes])

    @staticmethod
    def add_history_for_finished_site(site_id):
        """
        Додає історію роботи техніки при завершенні об'єкта.
        Беремо ВСЮ техніку, що була прив'язана до site_id,
        та записуємо один запис в історію із датами об'єкта.
        """

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT start_date, end_date
                FROM construction_sites
                WHERE id = %s;
            """, [site_id])
            row = cursor.fetchone()

        if not row:
            return

        site_start, site_end = row

        if not site_end:
            return

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, notes
                FROM equipment
                WHERE assigned_site_id = %s;
            """, [site_id])
            equipment_list = cursor.fetchall()

        with connection.cursor() as cursor:
            for eq_id, notes in equipment_list:
                cursor.execute("""
                    INSERT INTO equipment_work_history (equipment_id, site_id, start_date, end_date, notes)
                    VALUES (%s, %s, %s, %s, %s);
                """, [eq_id, site_id, site_start, site_end, notes])

    @staticmethod
    def finish_equipment_history_for_site(site_id):
        """
        Закриває або створює записи історії техніки при завершенні об'єкта.
        """

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT start_date, end_date
                FROM construction_sites
                WHERE id = %s;
            """, [site_id])
            row = cursor.fetchone()

        if not row:
            return

        site_start, site_end = row
        if not site_end:
            return

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, notes
                FROM equipment
                WHERE assigned_site_id = %s;
            """, [site_id])
            equipment_list = cursor.fetchall()

        with connection.cursor() as cursor:
            for eq_id, notes in equipment_list:

                cursor.execute("""
                    SELECT id
                    FROM equipment_work_history
                    WHERE equipment_id = %s
                      AND site_id = %s
                      AND end_date IS NULL;
                """, [eq_id, site_id])
                active = cursor.fetchone()

                if active:
                    cursor.execute("""
                        UPDATE equipment_work_history
                        SET end_date = %s
                        WHERE id = %s;
                    """, [site_end, active[0]])

                else:
                    cursor.execute("""
                        INSERT INTO equipment_work_history (equipment_id, site_id, start_date, end_date, notes)
                        VALUES (%s, %s, %s, %s, %s);
                    """, [eq_id, site_id, site_start, site_end, notes])