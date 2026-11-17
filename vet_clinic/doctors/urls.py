"""Маршруты приложения doctors."""
from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.doctors, name="list"),
]
