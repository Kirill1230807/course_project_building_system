from django.urls import path
from . import views

app_name = 'type_of_work'
urlpatterns = [

    path('', views.type_of_work, name='type_of_work'),
]