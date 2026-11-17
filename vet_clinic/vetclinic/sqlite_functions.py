"""Расширения Django ORM для SQLite (ПР9).

Встроенные LIKE и LOWER() в SQLite приводят к нижнему регистру только
латиницу, поэтому поиск «барс» не находил бы «Барсик». Модуль
регистрирует в каждом новом соединении функцию py_lower() и даёт
выражение PyLower для использования в запросах ORM.
"""
from django.db.backends.signals import connection_created
from django.db.models import CharField, Func
from django.dispatch import receiver


def _py_lower(value):
    """Привести строку к нижнему регистру средствами Python."""
    if isinstance(value, str):
        return value.lower()
    return value


@receiver(connection_created)
def register_py_lower(sender, connection, **kwargs):
    """Зарегистрировать py_lower() в соединении SQLite."""
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "py_lower", 1, _py_lower, deterministic=True
        )


class PyLower(Func):
    """SQL-выражение py_lower(поле): нижний регистр с учётом кириллицы."""

    function = "py_lower"

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=CharField(), **extra)
