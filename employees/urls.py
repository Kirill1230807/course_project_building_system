from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_employee, name='add'),
    path('delete/<int:employee_id>/', views.delete_employee, name='delete'),
    path('<int:employee_id>/', views.employee_detail, name='detail'),
    path("<int:employee_id>/edit/", views.edit_employee, name="edit"),

]
