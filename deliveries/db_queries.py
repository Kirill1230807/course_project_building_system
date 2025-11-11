from django.db import connection

class DeliveryQueries:
    @staticmethod
    def add_delivery(section_id, delivery_date, notes):
        """Створити нову доставку"""
        query = """
            INSERT INTO deliveries (section_id, supplier_id, delivery_date, notes, total_amount)
            VALUES (%s, (SELECT id FROM suppliers LIMIT 1), %s, %s, 0)
            RETURNING id;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [section_id, delivery_date, notes])
            return cursor.fetchone()[0]

    @staticmethod
    def add_delivery_item(delivery_id, material_id, quantity):
        """Додати позицію до доставки, з перевіркою залишку і оновленням складу"""
        with connection.cursor() as cursor:
            # Отримати поточну кількість і ціну матеріалу
            cursor.execute("""
                           SELECT count, price, supplier_id
                           FROM materials
                           WHERE id = %s;
                           """, [material_id])
            result = cursor.fetchone()

            if not result:
                raise ValueError("Матеріал не знайдено.")

            stock, price, supplier_id = result

            # Перевірити наявність
            if quantity > stock:
                raise ValueError(f"Недостатньо матеріалу на складі. Максимум можна замовити {stock} одиниць.")

            # Додати позицію доставки
            cursor.execute("""
                           INSERT INTO delivery_items (delivery_id, material_id, quantity, price_per_unit)
                           VALUES (%s, %s, %s, %s);
                           """, [delivery_id, material_id, quantity, price])

            # Прив’язати постачальника (якщо ще не заповнений)
            cursor.execute("""
                           UPDATE deliveries
                           SET supplier_id = %s
                           WHERE id = %s
                             AND supplier_id IS NULL;
                           """, [supplier_id, delivery_id])

            # Зменшити кількість на складі
            cursor.execute("""
                           UPDATE materials
                           SET count = count - %s
                           WHERE id = %s;
                           """, [quantity, material_id])
            # Оновити фактичне використання матеріалів у material_usage
            cursor.execute("""
                           INSERT INTO material_usage (section_id, material_id, used_qty)
                           VALUES ((SELECT section_id FROM deliveries WHERE id = %s),
                                   %s,
                                   %s)
                           ON CONFLICT (section_id, material_id)
                               DO UPDATE SET used_qty = material_usage.used_qty + EXCLUDED.used_qty;
                           """, [delivery_id, material_id, quantity])

    @staticmethod
    def update_total(delivery_id):
        """Оновити суму накладної"""
        query = """
            UPDATE deliveries
            SET total_amount = (
                SELECT COALESCE(SUM(total_price), 0)
                FROM delivery_items
                WHERE delivery_id = %s
            )
            WHERE id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [delivery_id, delivery_id])

    @staticmethod
    def get_reference_data():
        """Отримати списки для форми (об’єкти, матеріали з кількістю на складі)"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM construction_sites ORDER BY name;")
            sites = cursor.fetchall()

            cursor.execute("""
                           SELECT id, name, count
                           FROM materials
                           ORDER BY name;
                           """)
            materials = cursor.fetchall()

        return sites, materials

    @staticmethod
    def get_sections_by_site(site_id):
        """Отримати дільниці конкретного об’єкта"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM sections WHERE site_id = %s ORDER BY name;", [site_id])
            return cursor.fetchall()

    @staticmethod
    def get_deliveries(site_id=None, section_id=None, start_date=None, end_date=None):
        """Отримати список доставок з фільтрами"""
        query = """
            SELECT 
                d.id,
                cs.name AS site_name,
                s.name AS section_name,
                d.delivery_date,
                sup.name AS supplier_name,
                d.total_amount,
                d.notes
            FROM deliveries d
            LEFT JOIN sections s ON d.section_id = s.id
            LEFT JOIN construction_sites cs ON s.site_id = cs.id
            LEFT JOIN suppliers sup ON d.supplier_id = sup.id
            WHERE 1=1
        """
        params = []

        if site_id:
            query += " AND cs.id = %s"
            params.append(site_id)
        if section_id:
            query += " AND s.id = %s"
            params.append(section_id)
        if start_date:
            query += " AND d.delivery_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND d.delivery_date <= %s"
            params.append(end_date)

        query += " ORDER BY d.delivery_date DESC;"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            deliveries = cursor.fetchall()

        return deliveries

    @staticmethod
    def get_delivery_items(delivery_id):
        """Отримати матеріали (позиції) конкретної доставки"""
        query = """
            SELECT 
                m.name AS material_name,
                m.unit_id,
                u.short_name AS unit_name,
                di.quantity,
                di.price_per_unit,
                di.total_price
            FROM delivery_items di
            JOIN materials m ON di.material_id = m.id
            LEFT JOIN units u ON m.unit_id = u.id
            WHERE di.delivery_id = %s;
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [delivery_id])
            return cursor.fetchall()
