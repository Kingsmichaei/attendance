from django.urls import path
from .views import create_employee

urlpatterns = [
    path('create/', create_employee, name='create_employee'),
]
