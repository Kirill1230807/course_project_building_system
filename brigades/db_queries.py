from django.db import connection


class BrigadeQueries:
    """Запити до таблиці бригад"""

    @staticmethod
    def get_all():
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT b.id, b.name, e.last_name || ' ' || e.first_name AS leader, b.status, b.notes
                           FROM brigades b
                                    LEFT JOIN employees e ON b.leader_id = e.id
                           ORDER BY b.name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def get_by_id(brigade_id):
        """Отримати бригаду за ID"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT id, name, notes
                           FROM brigades
                           WHERE id = %s;
                           """, [brigade_id])
            row = cursor.fetchone()
        if not row:
            return None
        return {"id": row[0], "name": row[1], "notes": row[2]}

    @staticmethod
    def update(brigade_id, name, notes):
        """Оновити назву і примітки"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           UPDATE brigades
                           SET name  = %s,
                               notes = %s
                           WHERE id = %s;
                           """, [name, notes, brigade_id])

    @staticmethod
    def add(name, leader_id, status, notes):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO brigades (name, leader_id, status, notes)
                           VALUES (%s, %s, %s, %s);
                           """, [name, leader_id, status, notes])

    @staticmethod
    def delete(bid):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM brigades WHERE id = %s;", [bid])

    @staticmethod
    def get_members(brigade_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id, e.last_name, e.first_name, e.position_id, e.category, bm.role
                           FROM brigade_members bm
                                    JOIN employees e ON bm.employee_id = e.id
                           WHERE bm.brigade_id = %s;
                           """, [brigade_id])
            rows = cursor.fetchall()
        return [
            {"id": r[0], "last_name": r[1], "first_name": r[2],
             "position_id": r[3], "category": r[4], "role": r[5]}
            for r in rows
        ]

    @staticmethod
    def add_member(brigade_id, employee_id, role):
        with connection.cursor() as cursor:
            cursor.execute("""
                           INSERT INTO brigade_members (brigade_id, employee_id, role)
                           VALUES (%s, %s, %s);
                           """, [brigade_id, employee_id, role])

    @staticmethod
    def get_available_workers():
        """
        Повертає працівників категорії 'Робітники', які ще не входять у жодну бригаду:
        - не є бригадиром (leader_id)
        - не є членом жодної бригади (brigade_members)
        Додає до ПІБ посаду (наприклад: Іванов Іван — Маляр)
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.last_name || ' ' || e.first_name ||
                                  COALESCE(' ' || e.father_name, '') || ' -- ' || p.title AS full_name
                           FROM employees e
                                    JOIN positions p ON e.position_id = p.id
                           WHERE e.category = 'Робітники'
                             AND e.id NOT IN (SELECT leader_id
                                              FROM brigades
                                              WHERE leader_id IS NOT NULL
                                              UNION
                                              SELECT employee_id
                                              FROM brigade_members)
                           ORDER BY e.last_name, e.first_name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def is_employee_free(employee_id):
        """Перевіряє, чи працівник не входить до жодної бригади і не звільнений"""
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT COUNT(*)
                           FROM employees e
                           WHERE e.id = %s
                             AND e.end_date IS NULL
                             AND e.id NOT IN (SELECT leader_id
                                              FROM brigades
                                              WHERE leader_id IS NOT NULL
                                              UNION
                                              SELECT employee_id
                                              FROM brigade_members);
                           """, [employee_id])
            return cursor.fetchone()[0] > 0

    @staticmethod
    def is_available(brigade_id: int, for_section_id: int | None = None) -> bool:
        """
        True, якщо бригада не зайнята на іншій активній дільниці.
        Дозволяємо ту саму дільницю під час редагування.
        """
        with connection.cursor() as c:
            if for_section_id:
                c.execute("""
                          SELECT 1
                          FROM sections
                          WHERE brigade_id = %s
                            AND end_date IS NULL
                            AND id <> %s
                          LIMIT 1;
                          """, [brigade_id, for_section_id])
            else:
                c.execute("""
                          SELECT 1
                          FROM sections
                          WHERE brigade_id = %s
                            AND end_date IS NULL
                          LIMIT 1;
                          """, [brigade_id])
            return c.fetchone() is None

    @staticmethod
    def list_inactive_or_current(section_id: int | None = None):
        """
        Список бригад для селекта:
        - усі 'Неактивна'
        - + поточна бригада дільниці (щоб не зникала під час редагування)
        """
        params = []
        base = """
               SELECT b.id, b.name
               FROM brigades b
               WHERE b.status = 'Неактивна' \
               """
        if section_id:
            base += " OR b.id = (SELECT brigade_id FROM sections WHERE id = %s)"
            params.append(section_id)
        base += " ORDER BY b.name;"
        with connection.cursor() as c:
            c.execute(base, params)
            return c.fetchall()

    @staticmethod
    def get_available_workers_for_leader():
        """
        Повертає список працівників, які можуть бути бригадирами:
        - не є бригадирами у таблиці brigades
        - не входять до складу жодної бригади (brigade_members)
        Формат: [(id, "Прізвище Ім’я"), ...]
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                           SELECT e.id,
                                  e.last_name || ' ' || e.first_name AS full_name
                           FROM employees e
                           WHERE NOT EXISTS (SELECT 1
                                             FROM brigades b
                                             WHERE b.leader_id = e.id)
                             AND NOT EXISTS (SELECT 1
                                             FROM brigade_members bm
                                             WHERE bm.employee_id = e.id)
                           ORDER BY full_name;
                           """)
            return cursor.fetchall()

    @staticmethod
    def record_history_for_section(section_id, section_end_date):
        """
        Створює записи у brigade_work_history для всіх робіт дільниці.
        Викликається лише в момент завершення дільниці.
        """

        with connection.cursor() as c:

            # 1. Отримуємо бригаду, яка працювала на дільниці
            c.execute("""
                      SELECT brigade_id
                      FROM sections
                      WHERE id = %s;
                      """, [section_id])
            row = c.fetchone()

            if not row or not row[0]:
                # Немає бригади – записувати нічого
                return

            brigade_id = row[0]

            # 2. Отримуємо всі види робіт на дільниці
            c.execute("""
                      SELECT id,
                             COALESCE(actual_start, planned_start),
                             COALESCE(actual_end, planned_end)
                      FROM section_works
                      WHERE section_id = %s;
                      """, [section_id])

            works = c.fetchall()

            # 3. Записуємо історію
            for work in works:
                section_work_id = work[0]
                start_date = work[1]
                end_date = work[2] or section_end_date  # fallback якщо в роботі немає дати

                c.execute("""
                          INSERT INTO brigade_work_history
                              (brigade_id, section_work_id, start_date, end_date)
                          VALUES (%s, %s, %s, %s);
                          """, [
                              brigade_id,
                              section_work_id,
                              start_date,
                              end_date
                          ])