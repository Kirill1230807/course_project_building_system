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

    @staticmethod
    def get_by_id(material_id):
        """Отримати один матеріал за ID"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, description, supplier_id, price, count, unit_id
                           FROM materials
                           WHERE id = %s;
                           """, [material_id])
            row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "supplier_id": row[3],
            "price": row[4],
            "count": row[5],
            "unit_id": row[6],
        }

    @staticmethod
    def update(material_id, name, description, supplier_id, price, count, unit_id):
        """Оновити дані матеріалу"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE materials
                           SET name        = %s,
                               description = %s,
                               supplier_id = %s,
                               price       = %s,
                               count       = %s,
                               unit_id     = %s
                           WHERE id = %s;
                           """, [name, description, supplier_id, price, count, unit_id, material_id])


class SupplierQueries:
    """Прямі SQL-запити для таблиці suppliers"""

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

    @staticmethod
    def delete(supplier_id):
        """Видалити постачальника"""
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM suppliers WHERE id = %s;", [supplier_id])


class MaterialPlanQueries:
    @staticmethod
    def get_section_name(section_id: int):
        """Отримати назву дільниці"""
        with connection.cursor() as c:
            c.execute("SELECT name FROM sections WHERE id = %s;", [section_id])
            r = c.fetchone()
            return r[0] if r else None

    @staticmethod
    def get_all_materials():
        """Отримати список усіх матеріалів"""
        with connection.cursor() as c:
            c.execute("SELECT id, name FROM materials ORDER BY name;")
            return c.fetchall()

    @staticmethod
    def get_existing_plan(section_id: int):
        """Отримати існуючий кошторис для дільниці (щоб показати у формі)"""
        query = """
                SELECT m.id, m.name, COALESCE(p.planned_qty, 0)
                FROM materials m
                         LEFT JOIN material_plan p
                                   ON m.id = p.material_id AND p.section_id = %s
                ORDER BY m.name; \
                """
        with connection.cursor() as c:
            c.execute(query, [section_id])
            return c.fetchall()

    @staticmethod
    def save_plan(section_id: int, plan_data: list[tuple[int, float]]):
        """Зберегти кошторис для дільниці"""
        with connection.cursor() as c:
            c.execute("DELETE FROM material_plan WHERE section_id = %s;", [section_id])

            for material_id, qty in plan_data:
                c.execute("""
                          INSERT INTO material_plan (section_id, material_id, planned_qty)
                          VALUES (%s, %s, %s);
                          """, [section_id, material_id, qty])

    @staticmethod
    def get_site_id_by_section(section_id: int):
        """Повертає ID об’єкта, до якого належить дільниця"""
        with connection.cursor() as c:
            c.execute("SELECT site_id FROM sections WHERE id = %s;", [section_id])
            row = c.fetchone()
        return row[0] if row else None