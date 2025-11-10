from django.db import connection


class EquipmentQueries:
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.name,
                                  e.type,
                                  e.status,
                                  s.name AS site_name,
                                  e.notes
                           FROM equipment e
                                    LEFT JOIN construction_sites s ON e.assigned_site_id = s.id
                           ORDER BY e.id;
                           """)
            return cursor.fetchall()

    @staticmethod
    def add(name, type_, status, assigned_site_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO equipment (name, type, status, assigned_site_id, notes)
                           VALUES (%s, %s, %s, %s, %s);
                           """, [name, type_, status, assigned_site_id or None, notes])

    @staticmethod
    def delete(equipment_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM equipment WHERE id = %s;", [equipment_id])

    @staticmethod
    def get_by_id(equipment_id):
        """Отримати техніку за ID"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, type, status, assigned_site_id, notes
                           FROM equipment
                           WHERE id = %s;
                           """, [equipment_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "status": row[3],
            "assigned_site_id": row[4],
            "notes": row[5]
        }

    @staticmethod
    def update(equipment_id, name, type_, status, assigned_site_id, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE equipment
                           SET name             = %s,
                               type             = %s,
                               status           = %s,
                               assigned_site_id = %s,
                               notes            = %s
                           WHERE id = %s;
                           """, [name, type_, status, assigned_site_id or None, notes, equipment_id])
