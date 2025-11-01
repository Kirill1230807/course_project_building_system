from django.urls import path
from . import views

app_name = 'workplan'
urlpatterns = [
    path('', views.workplan, name='workplan'),
]
