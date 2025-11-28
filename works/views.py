from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from pyexpat.errors import messages
from .db_queries import WorkTypeQueries
from django.db import connection
from django.contrib import messages

def index(request):
    work_types = WorkTypeQueries.get_all()
    units = get_units()
    return render(request, "works/index.html", {"work_types": work_types, "units": units})

def add(request):
    """Додавання нового виду робіт"""
    if request.method == "POST":
        name = request.POST.get("name")
        unit_id = request.POST.get("unit_id")
        cost = request.POST.get("cost")

        if not (name and unit_id and cost):
            return HttpResponseBadRequest("Усі поля є обов'язковими!")

        WorkTypeQueries.add(name, unit_id, cost)
        messages.success(request, "Вид робіт створено!")
        return redirect("works:index")
    return redirect("works:index")

def edit(request, work_type_id):
    work_type = WorkTypeQueries.get_by_id(work_type_id)
    if not work_type:
        return HttpResponseNotFound("Вид робіт не знайдено")

    units = get_units()

    if request.method == "POST":
        name = request.POST.get("name")
        unit = request.POST.get("unit")
        cost = request.POST.get("cost")

        if not (name and unit and cost):
            return render(request, "works/edit.html", {
                "work_type": work_type,
                "units": units,
                "error_msg": "Усі поля є обов'язковими!"
            })

        WorkTypeQueries.update(work_type_id, name, unit, cost)
        messages.success(request, "Інформацію про вид робіт оновлено!")
        return redirect("works:index")

    return render(request, "works/edit.html", {"work_type": work_type, "units": units})

def delete(request, work_type_id):
    """Видалення виду робіт"""
    WorkTypeQueries.delete(work_type_id)
    messages.success(request, "Вид робіт видалено!")
    return redirect("works:index")

def get_units():
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, short_name FROM units ORDER BY id;")
        return cursor.fetchall()