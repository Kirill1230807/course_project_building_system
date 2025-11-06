from django.shortcuts import render
from django.db import connection

# Create your views here.
def home(request):
    # Підрахунок кількості об’єктів
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM construction_sites;")
        total_sites = cursor.fetchone()[0]

    # Підрахунок кількості працівників
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM employees;")
        total_employees = cursor.fetchone()[0]

    # Підрахунок кількості завершених об’єктів
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM construction_sites WHERE status = 'Завершено';")
        completed_sites = cursor.fetchone()[0]

    context = {
        "total_sites": total_sites,
        "total_employees": total_employees,
        "completed_sites": completed_sites,
    }

    return render(request, "core/home.html", context)

def about(request):
    return render(request, 'core/about.html')