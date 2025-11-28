from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from reports.db_queries import ReportQueries
from .db_queries import EquipmentQueries
from django.db import connection
from django.contrib import messages

def index(request):
    equipment = EquipmentQueries.get_all()
    types = EquipmentQueries.get_types()
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM construction_sites ORDER BY name;")
        sites = cursor.fetchall()

    return render(request, "equipment/index.html", {
        "equipment": equipment,
        "sites": sites,
        "types": types
    })

def add_equipment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        type_id = request.POST.get("type_id")
        status = request.POST.get("status")
        assigned_site_id = request.POST.get("assigned_site_id") or None
        notes = request.POST.get("notes") or ""

        EquipmentQueries.add(name, type_id, status, assigned_site_id, notes)

        with connection.cursor() as c:
            c.execute("SELECT MAX(id) FROM equipment;")
            equipment_id = c.fetchone()[0]

        if assigned_site_id:
            EquipmentQueries.add_history_entry(
                equipment_id=equipment_id,
                site_id=assigned_site_id,
                notes=notes
            )

        EquipmentQueries.update_status_based_on_site()

        return redirect("equipment:index")
    messages.success(request, "Техніку додано!")
    return redirect("equipment:index")

def edit_equipment(request, equipment_id):
    """Редагування техніки з логікою історії."""
    equipment = EquipmentQueries.get_by_id(equipment_id)
    if not equipment:
        return HttpResponseNotFound("Техніку не знайдено")

    types = EquipmentQueries.get_types()

    old_site_id = equipment["assigned_site_id"]
    old_notes = equipment["notes"]

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM construction_sites ORDER BY name;")
        sites = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        type_id = request.POST.get("type_id")
        status = request.POST.get("status") or ""
        new_site_id = request.POST.get("assigned_site_id") or None
        notes = request.POST.get("notes") or ""

        if new_site_id:
            if status not in ["В роботі", "В ремонті"]:
                status = "В роботі"
        else:
            if status not in ["Вільна", "В ремонті"]:
                status = "Вільна"

        site_changed = str(old_site_id) != str(new_site_id)

        if site_changed:

            if old_site_id:
                EquipmentQueries.close_active_history(equipment_id)

            if new_site_id not in ["", None]:
                EquipmentQueries.add_history_entry(
                    equipment_id=equipment_id,
                    site_id=new_site_id,
                    notes=notes
                )

        EquipmentQueries.update(
            equipment_id,
            name,
            type_id,
            status,
            new_site_id,
            notes
        )

        EquipmentQueries.update_status_based_on_site()
        messages.success(request, "Інформацію про техніку оновлено!")
        return redirect("equipment:index")

    return render(request, "equipment/edit.html", {
        "equipment": equipment,
        "types": types,
        "sites": sites
    })

def delete_equipment(request, equipment_id):
    EquipmentQueries.delete(equipment_id)
    messages.success(request, "Техніку видалено!")
    return redirect("equipment:index")

def report_equipment_history(request):
    site_id = request.GET.get("site_id")
    data = ReportQueries.get_equipment_history(site_id)

    with connection.cursor() as c:
        c.execute("SELECT id, name FROM construction_sites ORDER BY name")
        sites = c.fetchall()

    return render(request, "reports/report_equipment_site.html", {
        "sites": sites,
        "data": data,
        "selected_site": site_id
    })