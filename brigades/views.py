from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.db import connection
from .db_queries import BrigadeQueries
from django.contrib import messages

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

        if not name or not leader_id:
            return HttpResponseBadRequest("Вкажіть назву бригади та бригадира!")

        if not BrigadeQueries.is_employee_free(leader_id):
            return HttpResponseBadRequest("Цей працівник уже входить до іншої бригади!")

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brigades (name, leader_id, notes)
                VALUES (%s, %s, %s)
                RETURNING id;
            """, [name, leader_id, notes])
            brigade_id = cursor.fetchone()[0]

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO brigade_members (brigade_id, employee_id, role)
                VALUES (%s, %s, %s);
            """, [brigade_id, leader_id, "Бригадир"])

        messages.success(request, "Бригаду успішно створено!")
        return redirect("brigades:index")

    messages.success(request, "Бригаду успішно створено!")
    return redirect("brigades:index")

def edit_brigade(request, brigade_id):
    brigade = BrigadeQueries.get_by_id(brigade_id)
    if not brigade:
        return messages.error(request, "Бригаду не знайдено!")

    if request.method == "POST":
        name = request.POST.get("name")
        notes = request.POST.get("notes")

        if not name.strip():
            return render(request, "brigades/edit.html", {
                "brigade": brigade,
                "error_msg": "Назва не може бути порожньою."
            })

        BrigadeQueries.update(brigade_id, name, notes)
        messages.success(request, "Бригаду успішно оновлено!")
        return redirect("brigades:index")

    return render(request, "brigades/edit.html", {"brigade": brigade})

def delete_brigade(request, brigade_id):
    BrigadeQueries.delete(brigade_id)
    messages.success(request, "Бригаду успішно видалено!")
    return redirect("brigades:index")

def view_brigade(request, brigade_id):
    """Відображення детальної інформації про бригаду"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT b.id, b.name, e.last_name || ' ' || e.first_name AS leader, b.status, b.notes
            FROM brigades b
            LEFT JOIN employees e ON b.leader_id = e.id
            WHERE b.id = %s;
        """, [brigade_id])
        brigade = cursor.fetchone()

        if not brigade:
            return HttpResponseNotFound("Бригаду не знайдено")

        cursor.execute("""
            SELECT e.id, e.last_name || ' ' || e.first_name AS full_name, e.category, mb.role
            FROM brigade_members mb
            JOIN employees e ON mb.employee_id = e.id
            WHERE mb.brigade_id = %s;
        """, [brigade_id])
        members = cursor.fetchall()

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
    messages.success(request, "Працівника додано!")
    return redirect("brigades:view", brigade_id=brigade_id)

def remove_member(request, brigade_id, employee_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM brigade_members
            WHERE brigade_id = %s AND employee_id = %s;
        """, [brigade_id, employee_id])
    messages.success(request, "Працівника видалено!")
    return redirect("brigades:view", brigade_id=brigade_id)

def reassign_leader(request, brigade_id):
    """Перепризначення нового бригадира для бригади"""
    if request.method == "POST":
        new_leader_id = request.POST.get("new_leader_id")

        if not new_leader_id:
            return HttpResponseBadRequest("Не вибрано нового бригадира")

        with connection.cursor() as cursor:
            cursor.execute("SELECT leader_id FROM brigades WHERE id = %s;", [brigade_id])
            old_leader = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE brigades
                SET leader_id = %s
                WHERE id = %s;
            """, [new_leader_id, brigade_id])

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

            if old_leader:
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

                cursor.execute("""
                    UPDATE brigade_members
                    SET role = %s
                    WHERE brigade_id = %s AND employee_id = %s;
                """, [new_role, brigade_id, old_leader])
        messages.success(request, "Бригадира змінено!")
        return redirect("brigades:view", brigade_id=brigade_id)

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