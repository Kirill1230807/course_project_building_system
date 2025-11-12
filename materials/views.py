from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection, IntegrityError
from .db_queries import MaterialQueries, SupplierQueries, MaterialPlanQueries
from sites.db_queries import SectionQueries


def index(request):
    materials = MaterialQueries.get_all()
    suppliers_list = SupplierQueries.get_all()

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM suppliers ORDER BY name;")
        suppliers = cursor.fetchall()

        cursor.execute("SELECT id, name, short_name FROM units ORDER BY name;")
        units = cursor.fetchall()

    return render(request, "materials/index.html", {
        "materials": materials,
        "suppliers": suppliers,
        "suppliers_list": suppliers_list,
        "units": units
    })


def add_material(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description") or None
        supplier_id = request.POST.get("supplier_id")
        price = request.POST.get("price")
        count = request.POST.get("count")
        unit_id = request.POST.get("unit_id")

        if not (name and supplier_id and price and count and unit_id):
            return HttpResponseBadRequest("Не всі поля заповнені!")

        MaterialQueries.add(name, description, supplier_id, price, count, unit_id)
        return redirect("materials:index")

    return redirect("materials:index")


def delete_material(request, material_id):
    MaterialQueries.delete(material_id)
    return redirect("materials:index")


def add_supplier(request):
    if request.method == "POST":
        name = request.POST.get("name")
        contact_name = request.POST.get("contact_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")

        if not name:
            return HttpResponseBadRequest("Назва постачальника є обов’язковою!")

        SupplierQueries.add(name, contact_name, phone, email, address)
        return redirect("materials:index")

    return redirect("materials:index")


def edit_supplier(request, supplier_id):
    supplier = SupplierQueries.get_by_id(supplier_id)
    if not supplier:
        return HttpResponseNotFound("Постачальника не знайдено")

    if request.method == "POST":
        name = request.POST.get("name")
        contact_name = request.POST.get("contact_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        address = request.POST.get("address")

        if not name:
            return render(request, "materials/edit_supplier.html", {
                "supplier": supplier,
                "error_msg": "Назва компанії є обов’язковою!"
            })

        SupplierQueries.update(supplier_id, name, contact_name, phone, email, address)
        return redirect("materials:index")

    return render(request, "materials/edit_supplier.html", {"supplier": supplier})


def edit_material(request, material_id):
    """Редагування матеріалу"""
    material = MaterialQueries.get_by_id(material_id)
    if not material:
        return HttpResponseNotFound("Матеріал не знайдено")

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM suppliers ORDER BY name;")
        suppliers = cursor.fetchall()
        cursor.execute("SELECT id, name, short_name FROM units ORDER BY name;")
        units = cursor.fetchall()

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description") or None
        supplier_id = request.POST.get("supplier_id")
        price = request.POST.get("price")
        count = request.POST.get("count")
        unit_id = request.POST.get("unit_id")

        if not (name and supplier_id and price and count and unit_id):
            return render(request, "materials/edit_material.html", {
                "material": material,
                "suppliers": suppliers,
                "units": units,
                "error_msg": "Не всі поля заповнені!"
            })

        MaterialQueries.update(material_id, name, description, supplier_id, price, count, unit_id)
        return redirect("materials:index")

    return render(request, "materials/edit_material.html", {
        "material": material,
        "suppliers": suppliers,
        "units": units
    })


def delete_supplier(request, supplier_id):
    """Видалення постачальника з перевіркою зв'язків"""
    try:
        SupplierQueries.delete(supplier_id)
        return redirect("materials:index")
    except IntegrityError:
        return render(request, "materials/error_supplier_delete.html", {
            "message": "Неможливо видалити постачальника, бо він використовується у матеріалах."})

def add_material_plan(request, section_id):
    """Формування кошторису дільниці (введення планових матеріалів)"""
    section_name = MaterialPlanQueries.get_section_name(section_id)
    materials = MaterialPlanQueries.get_existing_plan(section_id)

    if request.method == "POST":
        material_ids = request.POST.getlist("material_id")
        planned_qtys = request.POST.getlist("planned_qty")

        plan_data = []
        for mid, qty in zip(material_ids, planned_qtys):
            try:
                qty_val = float(qty)
                if qty_val > 0:
                    plan_data.append((int(mid), qty_val))
            except ValueError:
                pass

        if not plan_data:
            messages.warning(request, "Не вказано жодного матеріалу з кількістю.")
        else:
            MaterialPlanQueries.save_plan(section_id, plan_data)
            messages.success(request, f"Кошторис для дільниці «{section_name}» збережено!")

            # Отримуємо site_id для цієї дільниці
            site_id = MaterialPlanQueries.get_site_id_by_section(section_id)

            # Повертаємо користувача до списку дільниць конкретного об’єкта
            return redirect("sites:sections", site_id=site_id)

    return render(request, "materials/add_material_plan.html", {
        "section_id": section_id,
        "section_name": section_name,
        "materials": materials,
    })