"""Маршруты приложения animals."""
from django.urls import path

from . import views

app_name = "animals"

urlpatterns = [
    path("", views.animals, name="list"),
    path("create/", views.animal_create, name="create"),
    path("<slug:slug>/", views.animal_detail, name="detail"),
]
