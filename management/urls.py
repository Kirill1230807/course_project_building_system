from django.urls import path
from . import views

app_name = "management"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_management, name="add_management"),
    path("delete/<int:management_id>/", views.delete_management, name="delete_management"),
    path("edit/<int:management_id>/", views.edit_management, name="edit_management"),

    # Інженери
    path("engineers/", views.engineers, name="engineers"),
    path("engineers/add/", views.add_engineer, name="add_engineer"),
    path("engineers/delete/<int:engineer_id>/", views.delete_engineer, name="delete_engineer"),
    path("engineers/edit/<int:engineer_id>/", views.edit_engineer, name="edit_engineer"),
]
