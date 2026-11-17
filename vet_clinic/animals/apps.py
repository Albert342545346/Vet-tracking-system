"""Конфигурация приложения animals."""
from django.apps import AppConfig


class AnimalsConfig(AppConfig):
    """Конфигурация приложения animals."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "animals"
    verbose_name = "Животные"

    def ready(self):
        """Подключить SQLite-функцию py_lower (поиск по кириллице)."""
        from vetclinic import sqlite_functions  # noqa: F401
