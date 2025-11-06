from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.db import connection
from .db_queries import BrigadeQueries
from employees.db_queries import EmployeeQueries


def index(request):
    brigades = BrigadeQueries.get_all()

    # Отримуємо всіх працівників (робітників), які можуть бути бригадирами
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, last_name || ' ' || first_name
            FROM employees
            WHERE category = 'Робітники'
            ORDER BY last_name;
        """)
        workers = cursor.fetchall()

    return render(request, "brigades/index.html", {
        "brigades": brigades,
        "workers": workers
    })


def add_brigade(request):
    if request.method == "POST":
        name = request.POST.get("name")
        leader_id = request.POST.get("leader_id") or None
        status = request.POST.get("status")
        notes = request.POST.get("notes") or None

        BrigadeQueries.add(name, leader_id, status, notes)
        return redirect("brigades:index")
    return redirect("brigades:index")


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

        # Отримуємо всіх працівників (щоб додавати до бригади)
        cursor.execute("""
            SELECT id, last_name || ' ' || first_name AS name
            FROM employees
            WHERE category = 'Робітники'
            ORDER BY last_name;
        """)
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
