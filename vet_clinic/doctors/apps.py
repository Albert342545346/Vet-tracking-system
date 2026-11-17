"""Конфигурация приложения doctors."""
from django.apps import AppConfig


class DoctorsConfig(AppConfig):
    """Конфигурация приложения doctors."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "doctors"
    verbose_name = "Врачи"
