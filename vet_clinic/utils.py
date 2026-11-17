"""Вспомогательные функции ввода данных с обработкой ошибок."""

from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число, повторяя запрос при ошибке."""
    while True:
        raw_value = input(prompt)
        try:
            return int(raw_value)
        except ValueError:
            print("Ошибка: введите целое число.")


def input_date(prompt: str) -> date:
    """Запросить у пользователя дату в формате ГГГГ-ММ-ДД."""
    while True:
        raw_value = input(prompt)
        try:
            return datetime.strptime(raw_value, "%Y-%m-%d").date()
        except ValueError:
            print("Ошибка: введите дату в формате ГГГГ-ММ-ДД.")
