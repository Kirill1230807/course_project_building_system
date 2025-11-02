from django.shortcuts import render, redirect
from django.db import connection
from .db_queries import BrigadeQueries
from employees.db_queries import EmployeeQueries


def index(request):
    brigades = BrigadeQueries.get_all()

    # отримуємо список працівників для вибору бригадира
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT id, last_name || ' ' || first_name AS full_name
                       FROM employees
                       ORDER BY last_name;
                       """)
        employees = cursor.fetchall()

    return render(request, "brigades/index.html", {
        "brigades": brigades,
        "employees": employees
    })


def add_brigade(request):
    if request.method == "POST":
        name = request.POST.get("name")
        leader_id = request.POST.get("leader_id")
        notes = request.POST.get("notes")
        status = request.POST.get("status", "Неактивна")

        BrigadeQueries.add(name, leader_id, notes, status)
        return redirect("brigades:index")

    return redirect("brigades:index")


def view_brigade(request, brigade_id):
    brigade_members = BrigadeQueries.get_members(brigade_id)

    # список усіх працівників для додавання
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT e.id,
                              e.last_name || ' ' || e.first_name AS full_name,
                              p.title                            AS position_name
                       FROM employees e
                                LEFT JOIN positions p ON e.position_id = p.id
                       ORDER BY e.last_name;
                       """)
        all_employees = cursor.fetchall()

    return render(request, "brigades/view.html", {
        "members": brigade_members,
        "brigade_id": brigade_id,
        "all_employees": all_employees
    })


def add_member(request, brigade_id):
    if request.method == "POST":
        employee_id = request.POST.get("employee_id")
        role = request.POST.get("role")
        BrigadeQueries.add_member(brigade_id, employee_id, role)
        return redirect("brigades:view", brigade_id=brigade_id)
