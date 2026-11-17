"""Маршруты приложения visits."""
from django.urls import path

from . import views

app_name = "visits"

urlpatterns = [
    path("", views.visits, name="list"),
    path("active/", views.active_visits, name="active"),
    path("available/", views.available_doctors, name="available"),
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.visit_create, name="create"),
    path("<int:visit_id>/", views.visit_detail, name="detail"),
    path("<int:visit_id>/edit/", views.visit_update, name="update"),
    path("<int:visit_id>/cancel/", views.visit_cancel, name="cancel"),
]
