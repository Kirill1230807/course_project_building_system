from django.urls import path
from . import views

app_name = "works"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("edit/<int:work_type_id>/", views.edit, name="edit"),
    path("delete/<int:work_type_id>/", views.delete, name="delete"),
]
