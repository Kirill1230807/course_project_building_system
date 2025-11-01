from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from .db_queries import EmployeeQueries
from django.db import connection



def index(request):
    employees = EmployeeQueries.get_all()

    # Отримуємо список посад для вибору
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, title, category FROM positions ORDER BY title;")
        positions = cursor.fetchall()

    return render(request, 'employees/index.html', {
        'employees': employees,
        'positions': positions
    })


def add_employee(request):
    if request.method == "POST":
        # 1️⃣ Отримуємо дані з форми
        form_data = {
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "father_name": request.POST.get("father_name", ""),
            "birthday": request.POST.get("birthday", ""),
            "start_date": request.POST.get("start_date", ""),
            "salary": request.POST.get("salary", ""),
            "position_id": request.POST.get("position_id", ""),
            "category": request.POST.get("category", "")
        }

        # 2️⃣ Отримуємо всі посади
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, category FROM positions ORDER BY title;")
            positions = cursor.fetchall()

        # 3️⃣ Отримуємо назву посади
        position_title = ""
        if form_data["position_id"]:
            with connection.cursor() as cursor:
                cursor.execute("SELECT title FROM positions WHERE id = %s;", [form_data["position_id"]])
                result = cursor.fetchone()
                if result:
                    position_title = result[0]

        # 4️⃣ Логічна перевірка
        error_msg = None
        if form_data["category"] == "Інженерно-технічний персонал" and position_title not in ["Головний інженер", "Начальник дільниці"]:
            error_msg = "Інженерно-технічний персонал може мати лише посади 'Головний інженер' або 'Начальник дільниці'."
        elif form_data["category"] == "Робітники" and position_title in ["Головний інженер", "Начальник дільниці"]:
            error_msg = "Робітники не можуть мати посаду 'Головний інженер' або 'Начальник дільниці'."
        elif not (form_data["first_name"] and form_data["last_name"] and form_data["salary"] and form_data["position_id"] and form_data["category"]):
            error_msg = "Не всі обов’язкові поля заповнені."

        # 5️⃣ Якщо є помилка — повертаємо форму з введеними даними
        if error_msg:
            employees = EmployeeQueries.get_all()
            return render(request, "employees/index.html", {
                "employees": employees,
                "positions": positions,
                "error_msg": error_msg,
                "form_data": form_data
            })

        # 6️⃣ Якщо все гаразд — додаємо працівника
        EmployeeQueries.add(
            form_data["first_name"],
            form_data["last_name"],
            form_data["father_name"],
            form_data["birthday"],
            form_data["start_date"],
            form_data["salary"],
            form_data["position_id"],
            form_data["category"]
        )

        return redirect("employees:index")

    return redirect("employees:index")

def delete_employee(request, employee_id):
    EmployeeQueries.delete(employee_id)
    return redirect('employees:index')

def employee_detail(request, employee_id):
    employee = EmployeeQueries.get_by_id(employee_id)
    if not employee:
        return HttpResponseNotFound("Працівника не знайдено")

    return render(request, "employees/detail.html", {"employee": employee})

def edit_employee(request, employee_id):
    if request.method == "GET":
        employee = EmployeeQueries.get_by_id(employee_id)
        if not employee:
            return HttpResponseNotFound("Працівника не знайдено")

        # Отримуємо всі посади (включно з категорією)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, category FROM positions ORDER BY title;")
            positions = cursor.fetchall()

        return render(request, "employees/edit.html", {
            "employee": employee,
            "positions": positions
        })

    elif request.method == "POST":
        data = request.POST
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        father_name = data.get("father_name") or None
        birthday = data.get("birthday")
        start_date = data.get("start_date")
        end_date = data.get("end_date") or None
        salary = data.get("salary")
        position_id = data.get("position_id")
        category = data.get("category")

        # Отримуємо назву посади
        with connection.cursor() as cursor:
            cursor.execute("SELECT title FROM positions WHERE id = %s;", [position_id])
            result = cursor.fetchone()
            position_title = result[0] if result else ""

        # Валідація категорії та посади
        if category == "Інженерно-технічний персонал" and position_title not in ["Головний інженер", "Начальник дільниці"]:
            error_msg = "Інженерно-технічний персонал може мати лише посади 'Головний інженер' або 'Начальник дільниці'."
        elif category == "Робітники" and position_title in ["Головний інженер", "Начальник дільниці"]:
            error_msg = "Робітники не можуть мати посаду 'Головний інженер' або 'Начальник дільниці'."
        else:
            error_msg = None

        if error_msg:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, title, category FROM positions ORDER BY title;")
                positions = cursor.fetchall()
            return render(request, "employees/edit.html", {
                "employee": {
                    "id": employee_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "father_name": father_name,
                    "birthday": birthday,
                    "start_date": start_date,
                    "end_date": end_date,
                    "salary": salary,
                    "position_id": position_id,
                    "category": category
                },
                "positions": positions,
                "error_msg": error_msg
            })

        # Оновлюємо дані
        EmployeeQueries.update(
            employee_id,
            first_name,
            last_name,
            father_name,
            birthday,
            start_date,
            end_date,
            salary,
            position_id,
            category
        )

        return redirect("employees:index")
