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
            # Без об'єкта → 'Вільна' (але не чіпаємо, якщо 'В ремонті')
            c.execute("""
                      UPDATE equipment
                      SET status = 'Вільна'
                      WHERE assigned_site_id IS NULL
                        AND status <> 'В ремонті';
                      """)
            # Прив'язана до об'єкта → 'В роботі' (але не чіпаємо, якщо 'В ремонті')
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
