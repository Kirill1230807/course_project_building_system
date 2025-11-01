from django.urls import path
from . import views

app_name = "materials"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_material, name="add"),
    path("delete/<int:material_id>/", views.delete_material, name="delete"),
    path("add-supplier/", views.add_supplier, name="add_supplier"),
]
