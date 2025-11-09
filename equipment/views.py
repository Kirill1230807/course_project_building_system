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
        status = request.POST.get("status")
        assigned_site_id = request.POST.get("assigned_site_id") or None
        notes = request.POST.get("notes") or ""

        EquipmentQueries.update(equipment_id, name, type_, status, assigned_site_id, notes)
        return redirect("equipment:index")

    return render(request, "equipment/edit.html", {"equipment": equipment, "sites": sites})