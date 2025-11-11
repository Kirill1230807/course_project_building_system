from django.urls import path
from . import views

app_name = "deliveries"
urlpatterns = [
    path("add/", views.add_delivery, name="add_delivery"),
    path("success/", views.add_delivery_success, name="add_delivery_success"),
    path("get-sections/<int:site_id>/", views.get_sections, name="get_sections"),
    path("list/", views.deliveries_list, name="deliveries_list"),
    path("detail/<int:delivery_id>/", views.delivery_detail, name="delivery_detail"),

]
