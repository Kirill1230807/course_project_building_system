from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import date
from django.contrib import messages
from .db_queries import DeliveryQueries
from django.db import connection


def add_delivery(request):
    sites, materials = DeliveryQueries.get_reference_data()

    if request.method == "POST":
        site_id = request.POST.get("site_id")
        section_id = request.POST.get("section_id")
        delivery_date = request.POST.get("delivery_date") or date.today()
        notes = request.POST.get("notes")

        material_ids = request.POST.getlist("material_id")
        quantities = request.POST.getlist("quantity")

        try:
            # створюємо накладну
            delivery_id = DeliveryQueries.add_delivery(section_id, delivery_date, notes)

            # додаємо позиції з перевіркою залишків
            for m_id, qty in zip(material_ids, quantities):
                if m_id and qty:
                    DeliveryQueries.add_delivery_item(delivery_id, int(m_id), float(qty))

            # оновлюємо суму
            DeliveryQueries.update_total(delivery_id)
            messages.success(request, "Доставку успішно створено!")
            return redirect("deliveries:add_delivery_success")

        except ValueError as e:
            # помилка (наприклад, забагато матеріалу)
            messages.error(request, str(e))
            return render(request, "deliveries/add_delivery.html", {
                "sites": sites,
                "materials": materials,
                "selected_site": site_id,
                "selected_section": section_id,
                "delivery_date": delivery_date,
                "notes": notes,
                "filled_materials": list(zip(material_ids, quantities)),
            })

    return render(request, "deliveries/add_delivery.html", {
        "sites": sites,
        "materials": materials,
    })


def get_sections(request, site_id):
    sections = DeliveryQueries.get_sections_by_site(site_id)
    return JsonResponse({"sections": sections})


def add_delivery_success(request):
    return render(request, "deliveries/success.html")


def deliveries_list(request):
    """Відображення всіх доставок із фільтрами"""
    sites, _ = DeliveryQueries.get_reference_data()

    site_id = request.GET.get("site_id")
    section_id = request.GET.get("section_id")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    deliveries = DeliveryQueries.get_deliveries(site_id, section_id, start_date, end_date)

    return render(request, "deliveries/deliveries_list.html", {
        "sites": sites,
        "deliveries": deliveries,
        "selected_site": site_id,
        "selected_section": section_id,
        "start_date": start_date,
        "end_date": end_date,
    })


def delivery_detail(request, delivery_id):
    """Детальна інформація про конкретну доставку"""
    with connection.cursor() as cursor:
        cursor.execute("""
                       SELECT d.id,
                              COALESCE(cs.name, '--')  AS site_name,
                              coalesce(s.name, '--')   AS section_name,
                              sup.name AS supplier_name,
                              d.delivery_date,
                              d.total_amount,
                              d.notes
                       FROM deliveries d
                                LEFT JOIN sections s ON d.section_id = s.id
                                LEFT JOIN construction_sites cs ON s.site_id = cs.id
                                LEFT JOIN suppliers sup ON d.supplier_id = sup.id
                       WHERE d.id = %s;
                       """, [delivery_id])
        delivery = cursor.fetchone()

    items = DeliveryQueries.get_delivery_items(delivery_id)

    return render(request, "deliveries/delivery_detail.html", {
        "delivery": delivery,
        "items": items
    })
