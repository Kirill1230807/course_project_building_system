from django.db import connection

from brigades.db_queries import BrigadeQueries


class SiteQueries:
    """Робота з таблицею construction_sites"""

    @staticmethod
    def get_all():
        """Отримати всі об’єкти будівництва"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT cs.id,
                                  cs.name,
                                  cs.address,
                                  cs.start_date,
                                  cs.end_date,
                                  cs.deadline,
                                  cs.status,
                                  cs.notes,
                                  m.name                             AS management_name,
                                  e.last_name || ' ' || e.first_name AS engineer_name

                           FROM construction_sites cs
                                    LEFT JOIN managements m ON cs.management_id = m.id
                                    LEFT JOIN employees e ON cs.responsible_engineer_id = e.id
                           ORDER BY cs.id;
                           """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(site_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id,
                                  name,
                                  address,
                                  start_date,
                                  end_date,
                                  deadline,
                                  status,
                                  notes,
                                  management_id,
                                  responsible_engineer_id
                           FROM construction_sites
                           WHERE id = %s;
                           """, [site_id])
            row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "address": row[2],
            "start_date": row[3],
            "end_date": row[4],
            "deadline": row[5],
            "status": row[6],
            "notes": row[7],
            "management_id": row[8],
            "responsible_engineer_id": row[9],
        }

    @staticmethod
    def add(name, address, start_date, end_date, deadline, management_id, responsible_engineer_id, status, notes):
        """Додати новий об’єкт"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO construction_sites
                           (name, address, start_date, end_date, deadline, management_id, responsible_engineer_id,
                            status, notes)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                           """, [name, address, start_date, end_date or None, deadline or None,
                                 management_id or None, responsible_engineer_id or None,
                                 status or 'В процесі', notes or None])

    @staticmethod
    def update(*, site_id, name, address, start_date, end_date, deadline,
               management_id, responsible_engineer_id, status, notes):
        """Оновити дані об’єкта"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE construction_sites
                           SET name                    = %s,
                               address                 = %s,
                               start_date              = %s,
                               end_date                = %s,
                               deadline                = %s,
                               management_id           = %s,
                               responsible_engineer_id = %s,
                               status                  = %s,
                               notes                   = %s
                           WHERE id = %s;
                           """, [name, address, start_date, end_date or None, deadline or None,
                                 management_id or None, responsible_engineer_id or None,
                                 status or 'В процесі', notes or None, site_id])
            if end_date and deadline and end_date > deadline:
                with connection.cursor() as c:
                    c.execute("UPDATE construction_sites SET status = 'Завершено із запізненням' WHERE id = %s;",
                              [site_id])

    @staticmethod
    def delete(site_id):
        """Видалити об’єкт"""
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM construction_sites WHERE id = %s;", [site_id])


# ======================================================================
# === 2. Робота з таблицею ДІЛЬНИЦЬ ====================================
# ======================================================================

class SectionQueries:
    @staticmethod
    def get_all(site_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT s.id,
                                  s.name,
                                  e.last_name || ' ' || e.first_name AS chief,
                                  b.name                             AS brigade,
                                  s.start_date,
                                  s.end_date,
                                  s.notes
                           FROM sections s
                                    LEFT JOIN employees e ON s.chief_id = e.id
                                    LEFT JOIN brigades b ON s.brigade_id = b.id
                           WHERE s.site_id = %s
                           ORDER BY s.id;
                           """, [site_id])
            return cursor.fetchall()

    @staticmethod
    def get_by_id(section_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id,
                                  name,
                                  site_id,
                                  chief_id,
                                  brigade_id,
                                  start_date,
                                  end_date,
                                  notes
                           FROM sections
                           WHERE id = %s;
                           """, [section_id])
            return cursor.fetchone()

    @staticmethod
    def add(name, site_id, chief_id, brigade_id, start_date, end_date, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO sections (name, site_id, chief_id, brigade_id, start_date, end_date, notes)
                           VALUES (%s, %s, %s, %s, %s, %s, %s);
                           """, [name, site_id, chief_id or None, brigade_id or None, start_date, end_date or None,
                                 notes or None])


    @staticmethod
    def update(section_id, name, chief_id, brigade_id, start_date, end_date, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE sections
                           SET name       = %s,
                               chief_id   = %s,
                               brigade_id = %s,
                               start_date = %s,
                               end_date   = %s,
                               notes      = %s
                           WHERE id = %s;
                           """,
                           [name, chief_id or None, brigade_id or None, start_date, end_date or None, notes or None,
                            section_id])

    @staticmethod
    def delete(section_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sections WHERE id=%s;", [section_id])


class SectionWorkQueries:
    """Запити для таблиці section_works"""

    @staticmethod
    def get_by_section(section_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT sw.id,
                                  wt.name,
                                  wt.cost_per_unit,
                                  sw.volume,
                                  sw.total_cost,
                                  sw.planned_start,
                                  sw.planned_end,
                                  sw.actual_start,
                                  sw.actual_end
                           FROM section_works sw
                                    JOIN work_types wt ON sw.work_type_id = wt.id
                           WHERE sw.section_id = %s
                           ORDER BY sw.id;
                           """, [section_id])
            return cursor.fetchall()

    @staticmethod
    def add(section_id, work_type_id, volume):
        with connection.cursor() as c:
            c.execute("""
                           INSERT INTO section_works (section_id, work_type_id, volume)
                           VALUES (%s, %s, %s);
                           """, [section_id, work_type_id, volume])

            section_work_id = c.fetchone()[0]

        # BrigadeQueries.register_brigade_history(section_work_id)

        return section_work_id


    @staticmethod
    def delete(work_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM section_works WHERE id = %s;", [work_id])

    @staticmethod
    def update_dates(work_id, planned_start, planned_end, actual_start, actual_end):
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE section_works
                           SET planned_start = %s,
                               planned_end   = %s,
                               actual_start  = %s,
                               actual_end    = %s
                           WHERE id = %s;
                           """, [
                               planned_start or None,
                               planned_end or None,
                               actual_start or None,
                               actual_end or None,
                               work_id
                           ])
