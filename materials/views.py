from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.db import connection, IntegrityError
from .db_queries import MaterialQueries, SupplierQueries


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
