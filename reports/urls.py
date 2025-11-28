from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path("", views.reports_menu, name="reports_menu"),
    path("site/<int:site_id>/schedule/", views.report_site_schedule_and_estimate, name="site_schedule"),
    path("brigades-by-work/", views.report_brigades_by_work, name="report_brigades_by_work"),
    path("materials/overbudget/", views.report_materials_overbudget, name="report_materials_overbudget"),
    path("sites-sections-managers/", views.report_sites_sections_managers, name="report_sites_sections_managers"),
    path("equipment-by-site/", views.report_equipment_by_site, name="report_equipment_by_site"),
    path("works-by-brigade/", views.report_works_by_brigade, name="report_works_by_brigade"),
    path("sites-by-management/", views.report_sites_by_management, name="report_sites_by_management"),
    path("delayed_works/", views.delayed_works_view, name="report_delayed_works"),
    path("brigade_staff/", views.brigade_staff_for_site_view, name="report_brigade_staff"),
    path("engineers/", views.engineers_view, name="report_engineers"),

]