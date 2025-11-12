from django.db import connection


class ReportQueries:
    @staticmethod
    def get_site_schedule_and_estimate(site_id: int):
        """Отримати графік і кошторис будівництва об’єкта."""
        query = """
                SELECT cs.id                                                 AS site_id,
                       cs.name                                               AS site_name,
                       cs.address,
                       cs.start_date                                         AS site_start,
                       cs.end_date                                           AS site_end,
                       cs.status,
                       s.id                                                  AS section_id,
                       s.name                                                AS section_name,
                       s.start_date                                          AS section_start,
                       s.end_date                                            AS section_end,
                       wt.name                                               AS work_name,
                       wt.cost_per_unit,
                       sw.volume,
                       COALESCE(sw.total_cost, wt.cost_per_unit * sw.volume) AS work_cost
                FROM construction_sites cs
                         LEFT JOIN sections s ON s.site_id = cs.id
                         LEFT JOIN section_works sw ON sw.section_id = s.id
                         LEFT JOIN work_types wt ON wt.id = sw.work_type_id
                WHERE cs.id = %s
                ORDER BY s.id, wt.name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [site_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_brigades_by_work_and_period(work_id=None, start_date=None, end_date=None):
        """
        Бригади, що виконували вказаний вид робіт у період,
        з вказанням об'єкта та дільниці.
        Дати беремо з sections.start_date / sections.end_date.
        Фільтр по періоду — умова перетину інтервалів.
        """
        query = """
                SELECT wt.name      AS work_name, \
                       b.name       AS brigade_name, \
                       cs.name      AS site_name, \
                       s.name       AS section_name, \
                       s.start_date AS section_start, \
                       s.end_date   AS section_end
                FROM section_works sw
                         JOIN work_types wt ON sw.work_type_id = wt.id
                         JOIN sections s ON sw.section_id = s.id
                         LEFT JOIN brigades b ON s.brigade_id = b.id
                         JOIN construction_sites cs ON s.site_id = cs.id
                WHERE 1 = 1 \
                """
        params = []

        if work_id:
            query += " AND wt.id = %s"
            params.append(work_id)

        # фільтр по періоду: перетин [s.start_date, s.end_date] з [start_date, end_date]
        if start_date and end_date:
            query += " AND s.start_date <= %s AND (s.end_date IS NULL OR s.end_date >= %s)"
            params.extend([end_date, start_date])
        elif start_date:
            query += " AND (s.end_date IS NULL OR s.end_date >= %s)"
            params.append(start_date)
        elif end_date:
            query += " AND s.start_date <= %s"
            params.append(end_date)

        query += " ORDER BY s.start_date NULLS LAST, site_name, section_name;"

        with connection.cursor() as c:
            c.execute(query, params)
            return c.fetchall()

    @staticmethod
    def get_materials_overbudget(section_id: int = None):
        """Отримати матеріали, де факт > план."""
        query = """
                SELECT m.name                       AS material_name, \
                       p.planned_qty, \
                       u.used_qty, \
                       (u.used_qty - p.planned_qty) AS overused_qty, \
                       s.name                       AS section_name, \
                       cs.name                      AS site_name
                FROM material_plan p
                         JOIN material_usage u
                              ON p.section_id = u.section_id AND p.material_id = u.material_id
                         JOIN materials m
                              ON m.id = p.material_id
                         JOIN sections s
                              ON s.id = p.section_id
                         JOIN construction_sites cs
                              ON cs.id = s.site_id
                WHERE u.used_qty > p.planned_qty
                  AND (%s IS NULL OR s.id = %s)
                ORDER BY overused_qty DESC; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [section_id, section_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_materials_for_site(site_id):
        """
        Отримати матеріали, доставлені на об'єкт (через дільниці)
        """
        query = """
                SELECT m.name              AS material_name, \
                       u.short_name        AS unit_name, \
                       SUM(di.quantity)    AS total_quantity, \
                       di.price_per_unit, \
                       SUM(di.total_price) AS total_cost
                FROM deliveries d
                         JOIN sections s ON d.section_id = s.id
                         JOIN construction_sites cs ON s.site_id = cs.id
                         JOIN delivery_items di ON di.delivery_id = d.id
                         JOIN materials m ON di.material_id = m.id
                         LEFT JOIN units u ON m.unit_id = u.id
                WHERE cs.id = %s
                GROUP BY m.name, u.short_name, di.price_per_unit
                ORDER BY m.name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [site_id])
            return cursor.fetchall()

    @staticmethod
    def get_sites_sections_managers():
        """
        Отримати перелік будівельних об'єктів, дільниць і керівників дільниць
        (з відображенням посади без телефону)
        """
        query = """
                SELECT cs.name                                                                   AS site_name, \
                       s.name                                                                    AS section_name, \
                       COALESCE(e.last_name || ' ' || e.first_name || ' ' || e.father_name, '—') AS manager_name, \
                       COALESCE(p.title, '—')                                                    AS position_name
                FROM sections s
                         JOIN construction_sites cs ON s.site_id = cs.id
                         LEFT JOIN employees e ON s.chief_id = e.id
                         LEFT JOIN positions p ON e.position_id = p.id
                ORDER BY cs.name, s.name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_equipment_by_site(site_id=None):
        """
        Отримати перелік будівельної техніки, закріпленої за об’єктами.
        Якщо задано site_id — фільтруємо по ньому.
        """
        query = """
                SELECT cs.name                AS site_name, \
                       e.name                 AS equipment_name, \
                       e.type                 AS equipment_type, \
                       e.status               AS equipment_status, \
                       COALESCE(e.notes, '--') AS equipment_notes
                FROM equipment e
                         LEFT JOIN construction_sites cs ON e.assigned_site_id = cs.id
                WHERE 1 = 1 \
                """
        params = []

        if site_id:
            query += " AND cs.id = %s"
            params.append(site_id)

        query += " ORDER BY cs.name, e.name;"

        with connection.cursor() as c:
            c.execute(query, params)
            cols = [col[0] for col in c.description]
            return [dict(zip(cols, row)) for row in c.fetchall()]

    @staticmethod
    def get_works_by_brigade_and_period(brigade_id=None, start_date=None, end_date=None):
        """
        Отримати перелік видів робіт, виконаних зазначеною бригадою у вказаний період
        з вказанням об'єкта і дільниці.
        """
        query = """
                SELECT b.name  AS brigade_name, \
                       wt.name AS work_name, \
                       cs.name AS site_name, \
                       s.name  AS section_name, \
                       s.start_date, \
                       s.end_date
                FROM section_works sw
                         JOIN work_types wt ON sw.work_type_id = wt.id
                         JOIN sections s ON sw.section_id = s.id
                         JOIN brigades b ON s.brigade_id = b.id
                         JOIN construction_sites cs ON s.site_id = cs.id
                WHERE 1 = 1 \
                """
        params = []

        if brigade_id:
            query += " AND b.id = %s"
            params.append(brigade_id)

        # Фільтр по датах (перетин інтервалів)
        if start_date and end_date:
            query += " AND s.start_date <= %s AND (s.end_date IS NULL OR s.end_date >= %s)"
            params.extend([end_date, start_date])
        elif start_date:
            query += " AND (s.end_date IS NULL OR s.end_date >= %s)"
            params.append(start_date)
        elif end_date:
            query += " AND s.start_date <= %s"
            params.append(end_date)

        query += " ORDER BY s.start_date NULLS LAST, site_name, section_name;"

        with connection.cursor() as c:
            c.execute(query, params)
            return c.fetchall()

    @staticmethod
    def get_sites_by_management_or_section(management_id=None):
        """
        Отримати перелік об’єктів і дільниць, які зводяться зазначеним управлінням
        (і графіки зведення: дати початку / завершення).
        """
        query = """
                SELECT m.name        AS management_name, \
                       cs.name       AS site_name, \
                       cs.address, \
                       cs.start_date AS site_start, \
                       cs.end_date   AS site_end, \
                       s.name        AS section_name, \
                       s.start_date  AS section_start, \
                       s.end_date    AS section_end
                FROM construction_sites cs
                         JOIN managements m ON cs.management_id = m.id
                         LEFT JOIN sections s ON s.site_id = cs.id
                WHERE 1 = 1 \
                """
        params = []

        if management_id:
            query += " AND m.id = %s"
            params.append(management_id)

        query += " ORDER BY m.name, cs.name, s.start_date NULLS LAST;"

        with connection.cursor() as c:
            c.execute(query, params)
            return c.fetchall()
