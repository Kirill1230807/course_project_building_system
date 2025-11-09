from django.urls import path
from . import views

app_name = "sites"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_site, name="add"),
    path("<int:site_id>/edit/", views.edit_site, name="edit"),
    path("<int:site_id>/delete/", views.delete_site, name="delete"),
    path("<int:site_id>/", views.detail_site, name="detail"),

    # Дільниці
    path("<int:site_id>/sections/", views.sections, name="sections"),
    path("<int:site_id>/sections/add/", views.add_section, name="add_section"),
    path("sections/<int:section_id>/edit/", views.edit_section, name="edit_section"),
    path("sections/<int:section_id>/delete/", views.delete_section, name="delete_section"),

    path("sections/<int:section_id>/works/", views.section_works, name="section_works"),
    path("sections/<int:section_id>/works/<int:work_id>/delete/", views.delete_section_work,
         name="delete_section_work"),

]
