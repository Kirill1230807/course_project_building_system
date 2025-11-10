from django.urls import path
from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_equipment, name="add"),
    path("delete/<int:equipment_id>/", views.delete_equipment, name="delete"),
    path("edit/<int:equipment_id>/", views.edit_equipment, name="edit"),
]
