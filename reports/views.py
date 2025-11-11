from django.shortcuts import render
from .db_queries import ReportQueries
from django.db import connection


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
