from django.urls import path
from . import views

app_name = 'reports'
urlpatterns = [
    path("", views.reports_menu, name="reports_menu"),
    path("site/<int:site_id>/schedule/", views.report_site_schedule_and_estimate, name="site_schedule"),
    path("brigades-by-work/", views.report_brigades_by_work, name="report_brigades_by_work"),
    path("materials/overbudget/", views.report_materials_overbudget, name="report_materials_overbudget"),

]
