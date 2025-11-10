from django.urls import path
from . import views

app_name = "materials"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_material, name="add"),
    path("edit/<int:material_id>/", views.edit_material, name="edit"),
    path("delete/<int:material_id>/", views.delete_material, name="delete"),
    path("add-supplier/", views.add_supplier, name="add_supplier"),
    path("suppliers/edit/<int:supplier_id>/", views.edit_supplier, name="edit_supplier"),
    path("supplier/delete/<int:supplier_id>/", views.delete_supplier, name="delete_supplier"),
]
