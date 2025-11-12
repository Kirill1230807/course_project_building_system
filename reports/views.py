from django.contrib import messages
from django.shortcuts import render
from .db_queries import ReportQueries
from django.db import connection
from equipment.db_queries import EquipmentQueries


def reports_menu(request):
    """Головна сторінка зі списком усіх звітів"""
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT id, name, address, status
                       FROM construction_sites
                       ORDER BY name;
                       """)
        sites = cursor.fetchall()

    return render(request, "reports/reports_menu.html", {"sites": sites})


def report_site_schedule_and_estimate(request, site_id):
    data = ReportQueries.get_site_schedule_and_estimate(site_id)
    if not data:
        return render(request, "reports/report_site_schedule.html", {"error": "Дані не знайдено."})

    site_info = {
        "name": data[0]["site_name"],
        "address": data[0]["address"],
        "start_date": data[0]["site_start"],
        "end_date": data[0]["site_end"],
        "status": data[0]["status"],
    }
    materials = ReportQueries.get_materials_for_site(site_id)
    materials_total = sum(row[4] for row in materials) if materials else 0
    cost_work = sum(row["work_cost"] or 0 for row in data)
    total_cost = cost_work + materials_total
    return render(
        request,
        "reports/report_site_schedule.html",
        {"site": site_info, "data": data, "total_cost": total_cost, "cost_work": cost_work, "materials": materials,
         "materials_total": materials_total},
    )


def report_brigades_by_work(request):
    works = []
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM work_types ORDER BY name;")
        works = cursor.fetchall()

    results = []
    if request.method == "GET" and ("work_id" in request.GET or "start_date" in request.GET):
        work_id = request.GET.get("work_id")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        if start_date and end_date and start_date > end_date:
            messages.warning(request, "Дата початку не може бути пізніше дати завершення.")
        else:
            results = ReportQueries.get_brigades_by_work_and_period(work_id, start_date, end_date)

    return render(request, "reports/report_brigades_work_period.html", {
        "works": works,
        "results": results
    })

def report_materials_overbudget(request):
    """Звіт: перевищення фактичного використання матеріалів над планом."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM sections ORDER BY name;")
        sections = cursor.fetchall()

    data = []
    selected_section = None

    if request.method == "POST":
        section_id = request.POST.get("section_id")
        selected_section = int(section_id) if section_id != "all" else None
        data = ReportQueries.get_materials_overbudget(selected_section)

    return render(request, "reports/report_materials_overbudget.html", {
        "sections": sections,
        "data": data,
        "selected_section": selected_section,
    })

def report_sites_sections_managers(request):
    """Звіт: Перелік об'єктів, дільниць і керівників"""
    data = ReportQueries.get_sites_sections_managers()
    return render(request, "reports/report_sites_sections_managers.html", {"data": data})

def report_equipment_by_site(request):
    """Звіт: перелік техніки за об’єктами"""
    EquipmentQueries.update_status_based_on_site()
    # Отримуємо список об’єктів для фільтра
    with connection.cursor() as c:
        c.execute("SELECT id, name FROM construction_sites ORDER BY name;")
        sites = c.fetchall()

    site_id = request.GET.get("site_id")
    data = ReportQueries.get_equipment_by_site(site_id)

    return render(request, "reports/report_equipment_site.html", {
        "sites": sites,
        "data": data,
        "selected_site": site_id,
    })

def report_works_by_brigade(request):
    """Звіт: Види робіт, виконані зазначеною бригадою у період"""
    with connection.cursor() as c:
        c.execute("SELECT id, name FROM brigades ORDER BY name;")
        brigades = c.fetchall()

    results = []
    if request.method == "GET" and ("brigade_id" in request.GET or "start_date" in request.GET):
        brigade_id = request.GET.get("brigade_id")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # перевірка коректності дат
        if start_date and end_date and start_date > end_date:
            messages.warning(request, "Дата початку не може бути пізніше дати завершення.")
        else:
            results = ReportQueries.get_works_by_brigade_and_period(brigade_id, start_date, end_date)

    return render(request, "reports/report_works_by_brigade.html", {
        "brigades": brigades,
        "results": results,
        "request": request,
    })

def report_sites_by_management(request):
    """Звіт: Об’єкти, що зводяться певним управлінням або дільницею"""
    with connection.cursor() as c:
        c.execute("SELECT id, name FROM managements ORDER BY name;")
        managements = c.fetchall()

    results = []
    if "management_id" in request.GET:
        management_id = request.GET.get("management_id")
        results = ReportQueries.get_sites_by_management_or_section(management_id)

    return render(request, "reports/report_sites_by_management.html", {
        "managements": managements,
        "results": results,
        "request": request
    })
