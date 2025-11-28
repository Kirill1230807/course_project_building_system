from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from .db_queries import ManagementQueries, EngineerQueries
from django.db import connection
from django.contrib import messages

def index(request):
    managements = ManagementQueries.get_all()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, last_name || ' ' || first_name FROM employees WHERE category='Інженерно-технічний персонал';")
        engineers = cursor.fetchall()
    return render(request, "management/index.html", {"managements": managements, "engineers": engineers})


def add_management(request):
    if request.method == "POST":
        name = request.POST.get("name")
        head_employee_id = request.POST.get("head_employee_id") or None
        notes = request.POST.get("notes") or ""
        ManagementQueries.add(name, head_employee_id, notes)
        return redirect("management:index")
    messages.success(request, "Будівельне керування створено!")
    return redirect("management:index")


def delete_management(request, management_id):
    ManagementQueries.delete(management_id)
    messages.success(request, "Будівельне керування видалено!")
    return redirect("management:index")


def edit_management(request, management_id):
    """Редагування будівельного управління"""
    management = ManagementQueries.get_by_id(management_id)
    if not management:
        return HttpResponseNotFound("Управління не знайдено")

    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT id, last_name || ' ' || first_name
                       FROM employees
                       WHERE category = 'Інженерно-технічний персонал';
                       """)
        engineers = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        head_employee_id = request.POST.get("head_employee_id") or None
        notes = request.POST.get("notes") or ""

        if not name:
            return render(request, "management/edit_management.html", {
                "management": management,
                "engineers": engineers,
                "error_msg": "Назва управління є обов’язковою!"
            })

        ManagementQueries.update(management_id, name, head_employee_id, notes)
        messages.success(request, "Інформацію про керування оновлено!")
        return redirect("management:index")

    return render(request, "management/edit_management.html", {
        "management": management,
        "engineers": engineers
    })


def engineers(request):
    all_engineers = EngineerQueries.get_all()

    active_engineers = [e for e in all_engineers if e["end_date"] is None]

    fired_engineers = [e for e in all_engineers if e["end_date"] is not None]

    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT id, title
                       FROM positions
                       WHERE category = 'Інженерно-технічний персонал'
                       ORDER BY title;
                       """)
        positions = cursor.fetchall()

    return render(request, "management/engineers.html", {
        "active_engineers": active_engineers,
        "fired_engineers": fired_engineers,
        "positions": positions
    })

def add_engineer(request):
    """Додавання нового інженера"""
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        father_name = request.POST.get("father_name") or None
        birthday = request.POST.get("birthday")
        start_date = request.POST.get("start_date")
        salary = request.POST.get("salary")
        position_id = request.POST.get("position_id")

        if not (first_name and last_name and salary and position_id):
            error_msg = "Не всі поля заповнені!"
            engineers = EngineerQueries.get_all()
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT id, title
                               FROM positions
                               WHERE category = 'Інженерно-технічний персонал';
                               """)
                positions = cursor.fetchall()
            return render(request, "management/engineers.html", {
                "engineers": engineers,
                "positions": positions,
                "error_msg": error_msg
            })

        EngineerQueries.add(first_name, last_name, father_name, birthday, start_date, salary, position_id)
        messages.success(request, "Інженера додано!")
        return redirect("management:engineers")

    return redirect("management:engineers")


def delete_engineer(request, engineer_id):
    """Видалення інженера"""
    EngineerQueries.delete(engineer_id)
    messages.success(request, "Інженера видалено!")
    return redirect("management:engineers")


def edit_engineer(request, engineer_id):
    """Редагування інженерно-технічного працівника"""
    engineer = EngineerQueries.get_by_id(engineer_id)
    if not engineer:
        return HttpResponseNotFound("Інженера не знайдено")

    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT id, title
                       FROM positions
                       WHERE category = 'Інженерно-технічний персонал'
                       ORDER BY title;
                       """)
        positions = cursor.fetchall()

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        father_name = request.POST.get("father_name") or None
        birthday = request.POST.get("birthday")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date") or None
        salary = request.POST.get("salary")
        position_id = request.POST.get("position_id")

        if not (first_name and last_name and salary and position_id):
            return render(request, "management/edit_engineer.html", {
                "engineer": engineer,
                "positions": positions,
                "error_msg": "Не всі поля заповнені!"
            })

        EngineerQueries.update(engineer_id, first_name, last_name, father_name, birthday, start_date, end_date, salary,
                               position_id)
        messages.success(request, "Інформацію про інженера оновлено!")
        return redirect("management:engineers")

    return render(request, "management/edit_engineer.html", {
        "engineer": engineer,
        "positions": positions
    })

def engineer_detail(request, engineer_id):
    engineer = EngineerQueries.get_by_id(engineer_id)
    if not engineer:
        return HttpResponseNotFound("Інженера не знайдено")

    # Отримуємо назву посади
    with connection.cursor() as cursor:
        cursor.execute("SELECT title FROM positions WHERE id = %s;", [engineer["position_id"]])
        pos = cursor.fetchone()
        position_title = pos[0] if pos else "—"

    return render(request, "management/detail_engineer.html", {
        "engineer": engineer,
        "position_title": position_title
    })