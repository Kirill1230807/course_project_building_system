from django.db import connection


class MaterialQueries:
    """Прямі SQL-запити для таблиці materials"""

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT m.id,
                                  m.name,
                                  m.description,
                                  m.price,
                                  m.count,
                                  u.short_name AS unit,
                                  s.name       AS supplier
                           FROM materials m
                                    JOIN units u ON m.unit_id = u.id
                                    JOIN suppliers s ON m.supplier_id = s.id
                           ORDER BY m.id;
                           """)
            rows = cursor.fetchall()
        return [
            {
                "id": r[0],
                "name": r[1],
                "description": r[2],
                "price": r[3],
                "count": r[4],
                "unit": r[5],
                "supplier": r[6]
            } for r in rows
        ]

    @staticmethod
    def add(name, description, supplier_id, price, count, unit_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO materials (name, description, supplier_id, price, count, unit_id)
                           VALUES (%s, %s, %s, %s, %s, %s);
                           """, [name, description, supplier_id, price, count, unit_id])

    @staticmethod
    def delete(material_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM materials WHERE id = %s;", [material_id])


class SupplierQueries:
    """Прямі SQL-запити для таблиці suppliers"""

    # показ постачальників
    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, contact_name, phone, email, address FROM suppliers ORDER BY name;")
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "name": r[1],
                    "contact_name": r[2],
                    "phone": r[3],
                    "email": r[4],
                    "address": r[5]
                } for r in rows
            ]

    # додавання постачальника
    @staticmethod
    def add(name, contact_name, phone, email, address):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO suppliers (name, contact_name, phone, email, address)
                           VALUES (%s, %s, %s, %s, %s);
                           """, [name, contact_name, phone, email, address])

    @staticmethod
    def get_by_id(supplier_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, contact_name, phone, email, address
                           FROM suppliers
                           WHERE id = %s;
                           """, [supplier_id])
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "contact_name": row[2],
            "phone": row[3],
            "email": row[4],
            "address": row[5]
        }

    @staticmethod
    def update(supplier_id, name, contact_name, phone, email, address):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE suppliers
                           SET name         = %s,
                               contact_name = %s,
                               phone        = %s,
                               email        = %s,
                               address      = %s
                           WHERE id = %s;
                           """, [name, contact_name, phone, email, address, supplier_id])