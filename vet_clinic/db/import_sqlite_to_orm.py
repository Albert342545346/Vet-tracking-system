"""Перенос данных из базы ПР7 (data/vetclinic.sqlite) в базу Django.

Исходная база не изменяется. Перед запуском примените миграции:
    python manage.py migrate
    python -m db.import_sqlite_to_orm

Идентификаторы сохраняются, порядок: животные, врачи, посещения,
назначения. Повторный запуск обновляет записи по первичному ключу.
"""
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "vetclinic.sqlite"


def setup_django():
    """Инициализировать Django при запуске скрипта из консоли."""
    sys.path.insert(0, str(BASE_DIR))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vetclinic.settings")
    import django

    django.setup()


def read_source(source_db):
    """Прочитать таблицы исходной базы (только чтение)."""
    with sqlite3.connect(source_db) as connection:
        connection.row_factory = sqlite3.Row
        return {
            "animals": connection.execute(
                "SELECT id, name, species, age, owner "
                "FROM animals ORDER BY id"
            ).fetchall(),
            "doctors": connection.execute(
                "SELECT id, name, specialization "
                "FROM doctors ORDER BY id"
            ).fetchall(),
            "visits": connection.execute(
                "SELECT id, animal_id, doctor_id, visit_date, "
                "diagnosis, is_cancelled FROM visits ORDER BY id"
            ).fetchall(),
            "prescriptions": connection.execute(
                "SELECT id, visit_id, medication, dosage, duration "
                "FROM prescriptions ORDER BY id"
            ).fetchall(),
        }


def transfer(source_db=SOURCE_DB):
    """Перенести данные одной транзакцией; вернуть число записей."""
    from django.db import transaction

    from animals.models import Animal
    from doctors.models import Doctor
    from visits.models import Prescription, Visit

    source_db = Path(source_db)
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")
    data = read_source(source_db)

    with transaction.atomic():
        for row in data["animals"]:
            Animal.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "species": row["species"],
                    "age": row["age"],
                    "owner": row["owner"],
                },
            )
        for row in data["doctors"]:
            Doctor.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "specialization": row["specialization"],
                },
            )
        for row in data["visits"]:
            status = (
                Visit.Status.CANCELLED
                if row["is_cancelled"]
                else Visit.Status.ACTIVE
            )
            Visit.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "animal_id": row["animal_id"],
                    "doctor_id": row["doctor_id"],
                    "visit_date": date.fromisoformat(row["visit_date"]),
                    "diagnosis": row["diagnosis"] or "",
                    "status": status,
                },
            )
        for row in data["prescriptions"]:
            Prescription.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "visit_id": row["visit_id"],
                    "medication": row["medication"],
                    "dosage": row["dosage"],
                    "duration": row["duration"],
                },
            )

    return {
        "animals": Animal.objects.count(),
        "doctors": Doctor.objects.count(),
        "visits": Visit.objects.count(),
        "prescriptions": Prescription.objects.count(),
    }


def main():
    setup_django()
    counts = transfer()
    print("Перенос данных завершён.")
    print(f"Животных: {counts['animals']}")
    print(f"Врачей: {counts['doctors']}")
    print(f"Посещений: {counts['visits']}")
    print(f"Назначений: {counts['prescriptions']}")


if __name__ == "__main__":
    main()
