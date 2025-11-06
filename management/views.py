from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from .db_queries import ManagementQueries, EngineerQueries
from django.db import connection

def index(request):
    managements = ManagementQueries.get_all()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, last_name || ' ' || first_name FROM employees WHERE category='Інженерно-технічний персонал';")
        engineers = cursor.fetchall()
    return render(request, "management/index.html", {"managements": managements, "engineers": engineers})

def add_management(request):
    if request.method == "POST":
        name = request.POST.get("name")
        head_employee_id = request.POST.get("head_employee_id") or None
        notes = request.POST.get("notes") or ""
        ManagementQueries.add(name, head_employee_id, notes)
        return redirect("management:index")
    return redirect("management:index")

def delete_management(request, management_id):
    ManagementQueries.delete(management_id)
    return redirect("management:index")

def engineers(request):
    """Відображення списку інженерно-технічного персоналу"""
    engineers = EngineerQueries.get_all()

    # Отримуємо всі посади, які належать до ІТП
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, title FROM positions 
            WHERE category = 'Інженерно-технічний персонал'
            ORDER BY title;
        """)
        positions = cursor.fetchall()

    return render(request, "management/engineers.html", {
        "engineers": engineers,
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

        # Перевірка обов’язкових полів
        if not (first_name and last_name and salary and position_id):
            error_msg = "Не всі поля заповнені!"
            engineers = EngineerQueries.get_all()
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, title FROM positions WHERE category = 'Інженерно-технічний персонал';
                """)
                positions = cursor.fetchall()
            return render(request, "management/engineers.html", {
                "engineers": engineers,
                "positions": positions,
                "error_msg": error_msg
            })

        # Додавання інженера
        EngineerQueries.add(first_name, last_name, father_name, birthday, start_date, salary, position_id)
        return redirect("management:engineers")

    return redirect("management:engineers")


def delete_engineer(request, engineer_id):
    """Видалення інженера"""
    EngineerQueries.delete(engineer_id)
    return redirect("management:engineers")