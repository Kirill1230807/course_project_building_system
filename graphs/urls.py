from django.urls import path
from . import views

app_name = 'graphs'
urlpatterns = [

    path('', views.graphs, name='graphs'),
]