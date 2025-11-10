from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection
from .db_queries import SiteQueries, SectionQueries, SectionWorkQueries


# ========================= ОБ'ЄКТИ =============================

def index(request):
    """Головна сторінка: список об’єктів будівництва"""
    sites = SiteQueries.get_all()

    # Для випадаючих списків у формі
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM managements ORDER BY name;")
        managements = cursor.fetchall()

        cursor.execute("""
                       SELECT id, last_name || ' ' || first_name
                       FROM employees
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
            sites = SiteQueries.get_all()
            return render(request, "sites/index.html", {"sites": sites, "error_msg": error_msg})

        SiteQueries.add(name, address, start_date, end_date, management_id, engineer_id, status, notes)
        return redirect("sites:index")

    return redirect("sites:index")


def delete_site(request, site_id):
    """Видалення об’єкта"""
    SiteQueries.delete(site_id)
    return redirect("sites:index")


def detail_site(request, site_id):
    # Отримуємо дані об’єкта
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT s.id,
                              s.name,
                              s.address,
                              s.start_date,
                              s.end_date,
                              s.status,
                              s.notes,
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
                       SELECT ss.id,
                              ss.name,
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
                       SELECT id,
                              name,
                              address,
                              start_date,
                              end_date,
                              management_id,
                              responsible_engineer_id,
                              status,
                              notes
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
                           SET name                    = %s,
                               address                 = %s,
                               start_date              = %s,
                               end_date                = %s,
                               management_id           = %s,
                               responsible_engineer_id = %s,
                               status                  = %s,
                               notes                   = %s
                           WHERE id = %s;
                           """,
                           [name, address, start_date, end_date, management_id, responsible_engineer_id, status, notes,
                            site_id])

        return redirect("sites:index")

    return render(request, "sites/edit_site.html", {
        "site": site,
        "managements": managements,
        "engineers": engineers
    })


# ========================== ДІЛЬНИЦІ ==============================

def sections(request, site_id):
    """Відображення дільниць для об’єкта"""
    sections = SectionQueries.get_all(site_id)

    with connection.cursor() as cursor:
        # тільки працівники ІТП, у яких посада 'Начальник дільниці'
        cursor.execute("""
                       SELECT e.id, e.last_name || ' ' || e.first_name AS full_name
                       FROM employees e
                                JOIN positions p ON e.position_id = p.id
                       WHERE e.category = 'Інженерно-технічний персонал'
                         AND LOWER(p.title) LIKE '%начальник дільниці%'
                       ORDER BY e.last_name, e.first_name;
                       """)
        chiefs = cursor.fetchall()

        cursor.execute("SELECT id, name FROM brigades ORDER BY name;")
        brigades = cursor.fetchall()

    return render(request, "sites/sections.html", {
        "sections": sections,
        "site_id": site_id,
        "chiefs": chiefs,
        "brigades": brigades
    })


def add_section(request, site_id):
    if request.method == "POST":
        name = request.POST.get("name")
        chief_id = request.POST.get("chief_id") or None
        brigade_id = request.POST.get("brigade_id") or None
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date") or None
        notes = request.POST.get("notes") or None

        if not (name and start_date):
            return HttpResponseBadRequest("Не всі обов’язкові поля заповнені!")

        SectionQueries.add(name, site_id, chief_id, brigade_id, start_date, end_date, notes)
        return redirect("sites:sections", site_id=site_id)
    return redirect("sites:sections", site_id=site_id)


def edit_section(request, section_id):
    row = SectionQueries.get_by_id(section_id)
    if not row:
        return HttpResponseNotFound("Дільницю не знайдено")

    section = {
        "id": row[0],
        "name": row[1],
        "site_id": row[2],
        "chief_id": row[3],
        "brigade_id": row[4],
        "start_date": row[5],
        "end_date": row[6],
        "notes": row[7],
    }

    # Отримуємо site_id або з таблиці, або з параметра GET
    site_id = request.GET.get("site_id") or section["site_id"]

    if request.method == "POST":
        name = request.POST.get("name")
        chief_id = request.POST.get("chief_id")
        brigade_id = request.POST.get("brigade_id")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        notes = request.POST.get("notes")

        SectionQueries.update(section_id, name, chief_id, brigade_id, start_date, end_date, notes)
        return redirect("sites:sections", site_id=site_id)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT e.id, e.last_name || ' ' || e.first_name AS full_name
            FROM employees e
                     JOIN positions p ON e.position_id = p.id
            WHERE e.category = 'Інженерно-технічний персонал'
              AND LOWER(p.title) LIKE '%начальник дільниці%'
            ORDER BY e.last_name, e.first_name;
        """)
        chiefs = cursor.fetchall()

        cursor.execute("SELECT id, name FROM brigades ORDER BY name;")
        brigades = cursor.fetchall()

    return render(request, "sites/edit_section.html", {
        "section": section,
        "chiefs": chiefs,
        "brigades": brigades
    })

def delete_section(request, section_id):
    section = SectionQueries.get_by_id(section_id)
    if not section:
        return HttpResponseNotFound("Дільницю не знайдено")

    site_id = request.GET.get("site_id") or section[2]

    SectionQueries.delete(section_id)
    return redirect("sites:sections", site_id=site_id)


# ========================== РОБОТА ==============================
def section_works(request, section_id):
    """Відображення або додавання робіт до конкретної дільниці"""
    # Отримуємо дані про дільницю
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.name, s.site_id
            FROM sections s
            WHERE s.id = %s;
        """, [section_id])
        section = cursor.fetchone()

    if not section:
        return HttpResponseNotFound("Дільницю не знайдено")

    section_data = {
        "id": section[0],
        "name": section[1],
        "site_id": section[2]
    }

    # Отримуємо site_id (із GET або з таблиці)
    site_id = request.GET.get("site_id") or section_data["site_id"]

    # Отримуємо список робіт на дільниці
    works = SectionWorkQueries.get_by_section(section_id)

    # Отримуємо типи робіт
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, name, cost_per_unit 
            FROM work_types
            ORDER BY name;
        """)
        work_types = cursor.fetchall()

    # Обчислення загальної суми робіт
    total_sum = sum(w[4] for w in works) if works else 0

    # Додавання нової роботи
    if request.method == "POST":
        work_type_id = request.POST.get("work_type_id")
        volume = request.POST.get("volume")

        if not work_type_id or not volume:
            return HttpResponseBadRequest("Усі поля є обов’язковими!")

        # Отримуємо ціну за одиницю
        with connection.cursor() as cursor:
            cursor.execute("SELECT cost_per_unit FROM work_types WHERE id = %s;", [work_type_id])
            cost_row = cursor.fetchone()

        if not cost_row:
            return HttpResponseBadRequest("Обраний вид роботи не знайдено!")

        cost_per_unit = cost_row[0]
        total_cost = float(cost_per_unit) * float(volume)

        # Додаємо запис у таблицю section_works
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO section_works (section_id, work_type_id, volume, total_cost)
                VALUES (%s, %s, %s, %s);
            """, [section_id, work_type_id, volume, total_cost])

        # Повертаємось до тієї ж сторінки
        return redirect(f"/sites/sections/{section_id}/works/?site_id={site_id}")

    return render(request, "sites/section_works.html", {
        "section": section_data,
        "works": works,
        "work_types": work_types,
        "site_id": site_id,
        "total_sum": total_sum
    })

def delete_section_work(request, section_id, work_id):
    """Видалення роботи з плану дільниці"""
    site_id = request.GET.get("site_id")

    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM section_works WHERE id = %s;", [work_id])

    return redirect(f"/sites/sections/{section_id}/works/?site_id={site_id}")
