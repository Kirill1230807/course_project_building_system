from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection
from .db_queries import ConstructionSiteQueries, SiteSectionQueries


# ========================= ОБ'ЄКТИ =============================

def index(request):
    """Головна сторінка: список об’єктів будівництва"""
    sites = ConstructionSiteQueries.get_all()

    # Для випадаючих списків у формі
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM managements ORDER BY name;")
        managements = cursor.fetchall()

        cursor.execute("""
            SELECT id, last_name || ' ' || first_name FROM employees 
            WHERE category = 'Інженерно-технічний персонал' 
            ORDER BY last_name;
        """)
        engineers = cursor.fetchall()

    return render(request, "sites/index.html", {
        "sites": sites,
        "managements": managements,
        "engineers": engineers,
    })


def add_site(request):
    """Додавання нового об’єкта"""
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date") or None
        management_id = request.POST.get("management_id") or None
        engineer_id = request.POST.get("responsible_engineer_id") or None
        status = request.POST.get("status") or "В процесі"
        notes = request.POST.get("notes") or None

        if not (name and address and start_date):
            error_msg = "Поля 'Назва', 'Адреса' і 'Дата початку' є обов’язковими!"
            sites = ConstructionSiteQueries.get_all()
            return render(request, "sites/index.html", {"sites": sites, "error_msg": error_msg})

        ConstructionSiteQueries.add(name, address, start_date, end_date, management_id, engineer_id, status, notes)
        return redirect("sites:index")

    return redirect("sites:index")


# def edit_site(request, site_id):
#     """Редагування об’єкта"""
#     site = ConstructionSiteQueries.get_by_id(site_id)
#     if not site:
#         return HttpResponseNotFound("Об’єкт не знайдено")
#
#     if request.method == "POST":
#         name = request.POST.get("name")
#         address = request.POST.get("address")
#         start_date = request.POST.get("start_date")
#         end_date = request.POST.get("end_date") or None
#         management_id = request.POST.get("management_id") or None
#         engineer_id = request.POST.get("responsible_engineer_id") or None
#         status = request.POST.get("status")
#         notes = request.POST.get("notes") or None
#
#         if not (name and address and start_date):
#             error_msg = "Не всі обов’язкові поля заповнені!"
#             return render(request, "sites/edit_site.html", {"site": site, "error_msg": error_msg})
#
#         ConstructionSiteQueries.update(site_id, name, address, start_date, end_date, management_id, engineer_id, status, notes)
#         return redirect("sites:index")
#
#     # Випадаючі списки
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT id, name FROM managements ORDER BY name;")
#         managements = cursor.fetchall()
#
#         cursor.execute("""
#             SELECT id, last_name || ' ' || first_name FROM employees
#             WHERE category = 'Інженерно-технічний персонал'
#             ORDER BY last_name;
#         """)
#         engineers = cursor.fetchall()
#
#     return render(request, "sites/edit_site.html", {
#         "site": site,
#         "managements": managements,
#         "engineers": engineers
#     })


def delete_site(request, site_id):
    """Видалення об’єкта"""
    ConstructionSiteQueries.delete(site_id)
    return redirect("sites:index")


# ========================== ДІЛЬНИЦІ ==============================

def sections(request, site_id):
    """Перегляд усіх дільниць конкретного об’єкта"""
    site = ConstructionSiteQueries.get_by_id(site_id)
    if not site:
        return HttpResponseNotFound("Об’єкт не знайдено")

    sections = SiteSectionQueries.get_all_for_site(site_id)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, last_name || ' ' || first_name FROM employees 
            WHERE category = 'Інженерно-технічний персонал' 
            ORDER BY last_name;
        """)
        engineers = cursor.fetchall()

    return render(request, "sites/sections.html", {
        "site": site,
        "sections": sections,
        "engineers": engineers
    })


def add_section(request, site_id):
    """Додати дільницю"""
    if request.method == "POST":
        name = request.POST.get("name")
        chief_id = request.POST.get("chief_employee_id") or None

        if not name:
            site = ConstructionSiteQueries.get_by_id(site_id)
            sections = SiteSectionQueries.get_all_for_site(site_id)
            error_msg = "Назва дільниці є обов’язковою!"
            return render(request, "sites/sections.html", {
                "site": site,
                "sections": sections,
                "error_msg": error_msg
            })

        SiteSectionQueries.add(name, site_id, chief_id)
        return redirect("sites:sections", site_id=site_id)

    return redirect("sites:sections", site_id=site_id)


def edit_section(request, section_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, site_id, name, chief_employee_id
            FROM site_sections WHERE id = %s;
        """, [section_id])
        section = cursor.fetchone()

    if not section:
        return HttpResponseNotFound("Дільницю не знайдено")

    section_data = {
        "id": section[0],
        "site_id": section[1],
        "name": section[2],
        "chief_employee_id": section[3]
    }

    # Отримуємо всіх інженерів
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, CONCAT(last_name, ' ', first_name, ' ', COALESCE(father_name, '')) AS full_name
            FROM employees
            WHERE category = 'Інженерно-технічний персонал'
            ORDER BY last_name;
        """)
        engineers = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        chief_id = request.POST.get("chief_employee_id") or None

        if not name:
            return render(request, "sites/edit_section.html", {
                "section": section_data,
                "engineers": engineers,
                "error_msg": "Назву дільниці обов’язково потрібно вказати!"
            })

        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE site_sections
                SET name = %s, chief_employee_id = %s
                WHERE id = %s;
            """, [name, chief_id, section_id])

        return redirect("sites:sections", site_id=section_data["site_id"])

    return render(request, "sites/edit_section.html", {
        "section": section_data,
        "engineers": engineers
    })



def delete_section(request, section_id, site_id):
    """Видалити дільницю"""
    SiteSectionQueries.delete(section_id)
    return redirect("sites:sections", site_id=site_id)

def detail_site(request, site_id):
    # Отримуємо дані об’єкта
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.name, s.address, s.start_date, s.end_date, s.status, s.notes,
                   e.last_name || ' ' || e.first_name || ' ' || COALESCE(e.father_name, '') AS engineer_name
            FROM construction_sites s
            LEFT JOIN employees e ON s.responsible_engineer_id = e.id
            WHERE s.id = %s;
        """, [site_id])
        row = cursor.fetchone()

    if not row:
        return HttpResponseNotFound("Об’єкт не знайдено")

    site = {
        "id": row[0],
        "name": row[1],
        "address": row[2],
        "start_date": row[3],
        "end_date": row[4],
        "status": row[5],
        "notes": row[6],
        "engineer_name": row[7],
    }

    # Отримуємо список дільниць цього об’єкта
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT ss.id, ss.name,
                   COALESCE(e.last_name || ' ' || e.first_name || ' ' || e.father_name, NULL) AS chief_name
            FROM site_sections ss
            LEFT JOIN employees e ON ss.chief_employee_id = e.id
            WHERE ss.site_id = %s
            ORDER BY ss.id;
        """, [site_id])
        sections = [
            {"id": r[0], "name": r[1], "chief_name": r[2]} for r in cursor.fetchall()
        ]

    return render(request, "sites/detail_site.html", {
        "site": site,
        "sections": sections
    })

def edit_site(request, site_id):
    # Отримуємо поточний об’єкт
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, address, start_date, end_date, management_id,
                   responsible_engineer_id, status, notes
            FROM construction_sites
            WHERE id = %s;
        """, [site_id])
        site_row = cursor.fetchone()

    if not site_row:
        return HttpResponseNotFound("Об’єкт не знайдено")

    site = {
        "id": site_row[0],
        "name": site_row[1],
        "address": site_row[2],
        "start_date": site_row[3],
        "end_date": site_row[4],
        "management_id": site_row[5],
        "responsible_engineer_id": site_row[6],
        "status": site_row[7],
        "notes": site_row[8],
    }

    # Отримуємо списки управлінь та інженерів
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM managements ORDER BY name;")
        managements = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, CONCAT(last_name, ' ', first_name, ' ', COALESCE(father_name, ''))
            FROM employees
            WHERE category = 'Інженерно-технічний персонал'
            ORDER BY last_name;
        """)
        engineers = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date") or None
        management_id = request.POST.get("management_id") or None
        responsible_engineer_id = request.POST.get("responsible_engineer_id") or None
        status = request.POST.get("status")
        notes = request.POST.get("notes")

        if not (name and address and start_date and status):
            return render(request, "sites/edit_site.html", {
                "site": site,
                "managements": managements,
                "engineers": engineers,
                "error_msg": "Заповніть усі обов’язкові поля!"
            })

        # Оновлення об’єкта
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE construction_sites
                SET name = %s,
                    address = %s,
                    start_date = %s,
                    end_date = %s,
                    management_id = %s,
                    responsible_engineer_id = %s,
                    status = %s,
                    notes = %s
                WHERE id = %s;
            """, [name, address, start_date, end_date, management_id, responsible_engineer_id, status, notes, site_id])

        return redirect("sites:index")

    return render(request, "sites/edit_site.html", {
        "site": site,
        "managements": managements,
        "engineers": engineers
    })