from django.db import connection


class ReportQueries:
    # 1) Графік і кошторис на будівництво об’єкта
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

    # 2) Перелік бригад, що виконали певний вид робіт у період
    @staticmethod
    def get_brigades_by_work_and_period(work_id=None, start_date=None, end_date=None):
        """
        Повертає бригади, які виконували певний вид робіт у вибраний період.
        Дані базуються на brigade_work_history.
        """

        query = """
                SELECT wt.name AS work_name, \
                       b.name  AS brigade_name, \
                       cs.name AS site_name, \
                       s.name  AS section_name, \
                       h.start_date, \
                       h.end_date
                FROM brigade_work_history h
                         JOIN section_works sw ON h.section_work_id = sw.id
                         JOIN work_types wt ON sw.work_type_id = wt.id
                         JOIN sections s ON sw.section_id = s.id
                         JOIN construction_sites cs ON s.site_id = cs.id
                         JOIN brigades b ON h.brigade_id = b.id
                WHERE 1 = 1 \
                """

        params = []

        # Фільтр по виду робіт
        if work_id:
            query += " AND wt.id = %s"
            params.append(work_id)

        # Дата: перетин діапазонів
        if start_date and end_date:
            query += " AND h.start_date <= %s AND (h.end_date IS NULL OR h.end_date >= %s)"
            params += [end_date, start_date]
        elif start_date:
            query += " AND (h.end_date IS NULL OR h.end_date >= %s)"
            params.append(start_date)
        elif end_date:
            query += " AND h.start_date <= %s"
            params.append(end_date)

        query += " ORDER BY h.start_date"

        with connection.cursor() as c:
            c.execute(query, params)
            return c.fetchall()

    # 4) Перелік матеріалів із перевищенням кошторису
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

    # 3) Перелік будівельних керувань / ділянок і керівників
    @staticmethod
    def get_sites_sections_managers():
        """
        Отримати перелік будівельних об'єктів, дільниць і керівників дільниць
        (з відображенням посади без телефону)
        """
        query = """
                SELECT cs.name                                                                    AS site_name, \
                       s.name                                                                     AS section_name, \
                       COALESCE(e.last_name || ' ' || e.first_name || ' ' || e.father_name, '--') AS manager_name, \
                       COALESCE(p.title, '--')                                                    AS position_name
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

    # 5) Перелік техніки, виділеної на об’єкт
    @staticmethod
    def get_equipment_history(site_id=None):
        query = """
                SELECT cs.name                 AS site_name, \
                       e.name                  AS equipment_name, \
                       et.title                AS equipment_type, \
                       h.start_date, \
                       h.end_date, \
                       COALESCE(h.notes, '--') AS notes
                FROM equipment_work_history h
                         JOIN equipment e ON h.equipment_id = e.id
                         LEFT JOIN equipment_types et ON e.type_id = et.id
                         LEFT JOIN construction_sites cs ON h.site_id = cs.id
                WHERE 1 = 1 \
                """
        params = []

        if site_id:
            query += " AND cs.id = %s"
            params.append(site_id)

        query += " ORDER BY h.start_date DESC;"

        with connection.cursor() as c:
            c.execute(query, params)
            cols = [col[0] for col in c.description]
            return [dict(zip(cols, row)) for row in c.fetchall()]

    # 6) Види робіт, виконані бригадою у період
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

    # 8) Об’єкти, що зводяться управлінням / ділянкою + графіки
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

    # 7) Види робіт із перевищенням термінів виконання
    @staticmethod
    def get_delayed_works():
        query = """
                SELECT wt.name                                      AS work_name, \
                       cs.name                                      AS site_name, \
                       s.name                                       AS section_name, \
                       sw.planned_start, \
                       sw.planned_end, \
                       sw.actual_start, \
                       sw.actual_end, \
                       (sw.actual_end::date - sw.planned_end::date) AS delay_days
                FROM section_works sw
                         JOIN work_types wt ON sw.work_type_id = wt.id
                         JOIN sections s ON sw.section_id = s.id
                         JOIN construction_sites cs ON s.site_id = cs.id
                WHERE sw.actual_end IS NOT NULL
                  AND sw.planned_end IS NOT NULL
                  AND sw.actual_end > sw.planned_end
                ORDER BY delay_days DESC; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_brigade_members_by_site(site_id):
        """Отримати склад бригад, що працювали на об’єкті."""
        query = """
                SELECT b.name                                                                   AS brigade_name,
                       e.last_name || ' ' || e.first_name || COALESCE(' ' || e.father_name, '') AS employee_name,
                       bm.role,
                       s.name                                                                   AS section_name
                FROM brigade_members bm
                         JOIN brigades b ON b.id = bm.brigade_id
                         JOIN employees e ON e.id = bm.employee_id
                         JOIN sections s ON s.id = b.section_id
                         JOIN construction_sites cs ON s.site_id = cs.id
                WHERE cs.id = %s
                ORDER BY brigade_name, employee_name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [site_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_engineers_by_section_or_management(section_id=None, management_id=None):
        """Отримати ІТП фахівців із зазначенням посад."""
        query = """
                SELECT e.last_name || ' ' || e.first_name || COALESCE(' ' || e.father_name, '') AS employee_name,
                       p.title                                                                  AS position_title,
                       s.name                                                                   AS section_name,
                       m.name                                                                   AS management_name
                FROM employees e
                         JOIN positions p ON e.position_id = p.id
                         LEFT JOIN sections s ON e.section_id = s.id
                         LEFT JOIN managements m ON s.management_id = m.id
                WHERE p.category = 'Інженерно-технічний персонал'
                  AND (%s IS NULL OR s.id = %s)
                  AND (%s IS NULL OR m.id = %s)
                ORDER BY management_name, section_name, employee_name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [section_id, section_id, management_id, management_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    @staticmethod
    def get_brigade_staff_for_site(site_id: int):
        query = """
                SELECT cs.name                                                                  AS site_name, \
                       b.id                                                                     AS brigade_id, \
                       b.name                                                                   AS brigade_name, \

                       e.id                                                                     AS employee_id, \
                       e.last_name || ' ' || e.first_name || COALESCE(' ' || e.father_name, '') AS employee_full_name, \

                       p.title                                                                  AS position_title, \
                       bm.role                                                                  AS brigade_role, \
                       bwh.start_date, \
                       bwh.end_date

                FROM construction_sites cs
                         JOIN sections s ON s.site_id = cs.id
                         JOIN section_works sw ON sw.section_id = s.id
                         JOIN brigade_work_history bwh ON bwh.section_work_id = sw.id
                         JOIN brigades b ON b.id = bwh.brigade_id
                         JOIN brigade_members bm ON bm.brigade_id = b.id
                         JOIN employees e ON e.id = bm.employee_id
                         LEFT JOIN positions p ON p.id = e.position_id

                WHERE cs.id = %s
                ORDER BY b.name, employee_full_name; \
                """
        with connection.cursor() as cursor:
            cursor.execute(query, [site_id])
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    # 10) ІТП фахівці по ділянці / управлінню
    @staticmethod
    def get_engineers_by_management_or_section(management_id=None, section_id=None):
        """
        Отримати список фахівців інженерно-технічного персоналу
        для зазначеної дільниці або управління.
        """
        query = """
                SELECT e.id                                                                     AS employee_id, \
                       e.last_name || ' ' || e.first_name || COALESCE(' ' || e.father_name, '') AS full_name, \
                       p.title                                                                  AS position_name, \
                       cs.name                                                                  AS site_name, \
                       s.name                                                                   AS section_name, \
                       m.name                                                                   AS management_name
                FROM employees e
                         JOIN positions p ON p.id = e.position_id
                         LEFT JOIN sections s ON s.chief_id = e.id
                         LEFT JOIN construction_sites cs ON cs.id = s.site_id
                         LEFT JOIN managements m ON m.id = cs.management_id
                WHERE p.category = 'Інженерно-технічний персонал' \
                """

        params = []

        if section_id:
            query += " AND s.id = %s"
            params.append(section_id)

        if management_id:
            query += " AND m.id = %s"
            params.append(management_id)

        query += " ORDER BY full_name;"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            cols = [col[0] for col in cursor.description]
            return [dict(zip(cols, row)) for row in cursor.fetchall()]

    # @staticmethod
    # def get_full_work_report(report_id: int):
    #     """Отримати повний звіт: загальні дані, матеріали, техніку."""
    #     result = {}
    #
    #     # 1) Основна інформація про звіт
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #                        SELECT wr.id,
    #                               wr.work_plan_id,
    #                               wr.actual_start,
    #                               wr.actual_end,
    #                               wr.actual_quantity,
    #                               wr.comment,
    #                               wp.section_id,
    #                               s.name  AS section_name,
    #                               wt.name AS work_name
    #                        FROM work_reports wr
    #                                 JOIN work_plans wp ON wr.work_plan_id = wp.id
    #                                 JOIN sections s ON wp.section_id = s.id
    #                                 JOIN work_types wt ON wp.work_type_id = wt.id
    #                        WHERE wr.id = %s;
    #                        """, [report_id])
    #
    #         cols = [col[0] for col in cursor.description]
    #         result["report"] = dict(zip(cols, cursor.fetchone()))
    #
    #     # 2) Матеріали
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #                        SELECT m.name                 AS material_name,
    #                               wrm.quantity,
    #                               m.price,
    #                               wrm.quantity * m.price AS total_cost
    #                        FROM work_report_materials wrm
    #                                 JOIN materials m ON wrm.material_id = m.id
    #                        WHERE wrm.report_id = %s
    #                        ORDER BY material_name;
    #                        """, [report_id])
    #
    #         cols = [col[0] for col in cursor.description]
    #         result["materials"] = [dict(zip(cols, row)) for row in cursor.fetchall()]
    #
    #     # 3) Техніка
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #                        SELECT e.name AS equipment_name,
    #                               e.type,
    #                               wre.quantity
    #                        FROM work_report_equipment wre
    #                                 JOIN equipment e ON wre.equipment_id = e.id
    #                        WHERE wre.report_id = %s
    #                        ORDER BY equipment_name;
    #                        """, [report_id])
    #
    #         cols = [col[0] for col in cursor.description]
    #         result["equipment"] = [dict(zip(cols, row)) for row in cursor.fetchall()]
    #
    #     return result
