from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.db import connection
from .db_queries import BrigadeQueries
from employees.db_queries import EmployeeQueries


def index(request):
    """Список бригад + модальне вікно для створення"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.id, b.name, 
                   e.last_name || ' ' || e.first_name AS leader,
                   b.status, b.notes
            FROM brigades b
            LEFT JOIN employees e ON b.leader_id = e.id
            ORDER BY b.id;
        """)
        brigades = cursor.fetchall()

    # отримуємо лише вільних працівників
    available_workers = BrigadeQueries.get_available_workers()

    return render(request, "brigades/index.html", {
        "brigades": brigades,
        "workers": available_workers,
    })

def add_brigade(request):
    """Створення нової бригади (статус визначається автоматично)"""
    leaders = BrigadeQueries.get_available_workers_for_leader()

    if request.method == "POST":
        name = request.POST.get("name")
        leader_id = request.POST.get("leader_id")
        notes = request.POST.get("notes") or None

        if not BrigadeQueries.get_available_workers_for_leader():
            return HttpResponseBadRequest("Оберіть бригадира!")

        # Перевірка заповнення обов’язкових полів
        if not name or not leader_id:
            return HttpResponseBadRequest("Вкажіть назву бригади та бригадира!")

        # Перевірка, чи працівник уже не є бригадиром або членом іншої бригади
        if not BrigadeQueries.is_employee_free(leader_id):
            return HttpResponseBadRequest("Цей працівник уже входить до іншої бригади!")

        # Додаємо нову бригаду (статус за замовчуванням 'Неактивна')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brigades (name, leader_id, notes)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, [name, leader_id, notes])
            brigade_id = cursor.fetchone()[0]

        # Автоматично додаємо бригадира у склад бригади
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brigade_members (brigade_id, employee_id, role)
                VALUES (%s, %s, %s);
            """, [brigade_id, leader_id, "Бригадир"])

        return redirect("brigades:index")

    # fallback, якщо GET-запит
    return redirect("brigades:index")

def edit_brigade(request, brigade_id):
    brigade = BrigadeQueries.get_by_id(brigade_id)
    if not brigade:
        return render(request, "brigades/error.html", {"message": "Бригаду не знайдено."})

    if request.method == "POST":
        name = request.POST.get("name")
        notes = request.POST.get("notes")

        if not name.strip():
            return render(request, "brigades/edit.html", {
                "brigade": brigade,
                "error_msg": "Назва не може бути порожньою."
            })

        BrigadeQueries.update(brigade_id, name, notes)
        return redirect("brigades:index")  # після редагування — повертаємось до списку

    return render(request, "brigades/edit.html", {"brigade": brigade})

def delete_brigade(request, brigade_id):
    BrigadeQueries.delete(brigade_id)
    return redirect("brigades:index")

def view_brigade(request, brigade_id):
    """Відображення детальної інформації про бригаду"""
    with connection.cursor() as cursor:
        # Отримуємо інформацію про бригаду
        cursor.execute("""
            SELECT b.id, b.name, e.last_name || ' ' || e.first_name AS leader, b.status, b.notes
            FROM brigades b
            LEFT JOIN employees e ON b.leader_id = e.id
            WHERE b.id = %s;
        """, [brigade_id])
        brigade = cursor.fetchone()

        if not brigade:
            return HttpResponseNotFound("Бригаду не знайдено")

        # Отримуємо учасників бригади
        cursor.execute("""
            SELECT e.id, e.last_name || ' ' || e.first_name AS full_name, e.category, mb.role
            FROM brigade_members mb
            JOIN employees e ON mb.employee_id = e.id
            WHERE mb.brigade_id = %s;
        """, [brigade_id])
        members = cursor.fetchall()

        # Отримуємо працівників, які можна додати:
        # - категорія "Робітники"
        # - не мають end_date
        # - не входять у поточну бригаду
        cursor.execute("""
            SELECT e.id,
                   e.last_name || ' ' || e.first_name ||
                   COALESCE(' — ' || p.title, '') AS name
            FROM employees e
            JOIN positions p ON e.position_id = p.id
            WHERE e.category = 'Робітники'
              AND e.end_date IS NULL
              AND e.id NOT IN (
                  SELECT employee_id FROM brigade_members WHERE brigade_id = %s
              )
            ORDER BY e.last_name, e.first_name;
        """, [brigade_id])
        employees = cursor.fetchall()

    return render(request, "brigades/view.html", {
        "brigade": brigade,
        "members": members,
        "employees": employees
    })


def add_member(request, brigade_id):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        role = request.POST.get("role")
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brigade_members (brigade_id, employee_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, [brigade_id, employee_id, role])
    return redirect("brigades:view", brigade_id=brigade_id)

def remove_member(request, brigade_id, employee_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM brigade_members
            WHERE brigade_id = %s AND employee_id = %s;
        """, [brigade_id, employee_id])
    return redirect("brigades:view", brigade_id=brigade_id)

def reassign_leader(request, brigade_id):
    """Перепризначення нового бригадира для бригади"""
    if request.method == "POST":
        new_leader_id = request.POST.get("new_leader_id")

        if not new_leader_id:
            return HttpResponseBadRequest("Не вибрано нового бригадира")

        with connection.cursor() as cursor:
            # Отримуємо поточного (старого) бригадира
            cursor.execute("SELECT leader_id FROM brigades WHERE id = %s;", [brigade_id])
            old_leader = cursor.fetchone()[0]

            # Оновлюємо нового лідера в таблиці brigades
            cursor.execute("""
                UPDATE brigades
                SET leader_id = %s
                WHERE id = %s;
            """, [new_leader_id, brigade_id])

            # Додаємо або оновлюємо нового бригадира в brigade_members
            cursor.execute("""
                SELECT COUNT(*) FROM brigade_members
                WHERE brigade_id = %s AND employee_id = %s;
            """, [brigade_id, new_leader_id])
            exists = cursor.fetchone()[0]

            if not exists:
                cursor.execute("""
                    INSERT INTO brigade_members (brigade_id, employee_id, role)
                    VALUES (%s, %s, %s);
                """, [brigade_id, new_leader_id, "Бригадир"])
            else:
                cursor.execute("""
                    UPDATE brigade_members
                    SET role = %s
                    WHERE brigade_id = %s AND employee_id = %s;
                """, ["Бригадир", brigade_id, new_leader_id])

            # Якщо старий бригадир існував — оновлюємо його роль
            if old_leader:
                # Отримуємо його посаду (title)
                cursor.execute("""
                    SELECT p.title
                    FROM employees e
                    JOIN positions p ON e.position_id = p.id
                    WHERE e.id = %s;
                """, [old_leader])
                position = cursor.fetchone()

                if position:
                    new_role = position[0]
                else:
                    new_role = "Робітник"

                # Якщо старий бригадир є у складі, оновлюємо його роль
                cursor.execute("""
                    UPDATE brigade_members
                    SET role = %s
                    WHERE brigade_id = %s AND employee_id = %s;
                """, [new_role, brigade_id, old_leader])

        return redirect("brigades:view", brigade_id=brigade_id)

    # --- GET-запит: показуємо кандидатів ---
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id,
                   e.last_name || ' ' || e.first_name ||
                   COALESCE(' ' || e.father_name, '') ||
                   ' (' || p.title || ')' AS name
            FROM employees e
            JOIN positions p ON e.position_id = p.id
            WHERE e.end_date IS NULL
              AND e.category = 'Робітники'
              AND (
                    e.id IN (SELECT employee_id FROM brigade_members WHERE brigade_id = %s)
                    OR e.id NOT IN (
                        SELECT leader_id FROM brigades WHERE leader_id IS NOT NULL
                        UNION
                        SELECT employee_id FROM brigade_members
                    )
                  )
            ORDER BY e.last_name, e.first_name;
        """, [brigade_id])
        candidates = cursor.fetchall()

    return render(request, "brigades/reassign_leader.html", {
        "brigade_id": brigade_id,
        "candidates": candidates
    })
