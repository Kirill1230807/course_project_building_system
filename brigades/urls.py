from django.urls import path
from . import views

app_name = "brigades"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_brigade, name="add"),
    path("<int:brigade_id>/", views.view_brigade, name="view"),
    path("<int:brigade_id>/add_member/", views.add_member, name="add_member"),
]
