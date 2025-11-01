from django.urls import path
from . import views

app_name = 'brigades'
urlpatterns = [

    path('', views.brigades, name='brigades'),
]