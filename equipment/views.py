from django.shortcuts import render, redirect
from .db_queries import EquipmentQueries
from django.db import connection


def index(request):
    equipment = EquipmentQueries.get_all()

    # список об’єктів для вибору
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM construction_sites ORDER BY name;")
        sites = cursor.fetchall()

    return render(request, "equipment/index.html", {
        "equipment": equipment,
        "sites": sites
    })


def add_equipment(request):
    if request.method == "POST":
        name = request.POST.get("name")
        type_ = request.POST.get("type")
        status = request.POST.get("status")
        assigned_site_id = request.POST.get("assigned_site_id") or None
        notes = request.POST.get("notes") or ""

        EquipmentQueries.add(name, type_, status, assigned_site_id, notes)
        EquipmentQueries.update_status_based_on_site()
        return redirect("equipment:index")
    return redirect("equipment:index")


def delete_equipment(request, equipment_id):
    EquipmentQueries.delete(equipment_id)
    return redirect("equipment:index")


def edit_equipment(request, equipment_id):
    """Редагування техніки"""
    equipment = EquipmentQueries.get_by_id(equipment_id)

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM construction_sites ORDER BY name;")
        sites = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        type_ = request.POST.get("type")
        status = request.POST.get("status") or ""
        assigned_site_id = request.POST.get("assigned_site_id") or None
        notes = request.POST.get("notes") or ""

        # --- Правила логіки ---
        if assigned_site_id:
            # Прив’язана → дозволено “В роботі” або “В ремонті”
            if status not in ["В роботі", "В ремонті"]:
                status = "В роботі"
        else:
            # Не прив’язана → дозволено “Вільна” або “В ремонті”
            if status not in ["Вільна", "В ремонті"]:
                status = "Вільна"

        EquipmentQueries.update(equipment_id, name, type_, status, assigned_site_id, notes)
        EquipmentQueries.update_status_based_on_site()
        return redirect("equipment:index")

    return render(request, "equipment/edit.html", {"equipment": equipment, "sites": sites})