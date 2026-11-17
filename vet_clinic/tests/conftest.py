"""Фикстуры для тестов: слой SQLite (ПР7) и модели Django (ПР9–ПР11)."""
import json
import sqlite3
from datetime import date, timedelta
from types import SimpleNamespace

import pytest

from db.database import get_connection, init_db
from db.import_json import import_all

ANIMALS = [
    {"id": 1, "name": "Барсик", "species": "кошка", "age": 3,
     "owner": "Иванов И.И."},
    {"id": 2, "name": "Рекс", "species": "собака", "age": 5,
     "owner": "Петрова А.С."},
    {"id": 3, "name": "Мурка", "species": "кошка", "age": 7,
     "owner": "Смирнова Е.А."},
]
DOCTORS = [
    {"id": 1, "name": "Сидоров П.П.", "specialization": "терапевт"},
    {"id": 2, "name": "Кузнецова О.В.", "specialization": "хирург"},
]
VISITS = [
    {"id": 1, "animal_id": 1, "doctor_id": 1, "date": "2026-10-15",
     "diagnosis": "Гастрит", "is_cancelled": False,
     "prescriptions": [
         {"medication": "Омепразол", "dosage": "1 таб.",
          "duration": "5 дней"},
     ]},
    {"id": 2, "animal_id": 2, "doctor_id": 1, "date": "2026-10-16",
     "diagnosis": "", "is_cancelled": True, "prescriptions": []},
    {"id": 3, "animal_id": 3, "doctor_id": 2, "date": "2026-10-15",
     "diagnosis": "", "is_cancelled": False, "prescriptions": []},
]


def _write(path, data):
    """Записать тестовые данные в JSON-файл."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
    return str(path)


@pytest.fixture
def json_files(tmp_path):
    """Тестовые JSON-файлы: (животные, врачи, посещения)."""
    return (
        _write(tmp_path / "animals.json", ANIMALS),
        _write(tmp_path / "doctors.json", DOCTORS),
        _write(tmp_path / "visits.json", VISITS),
    )


@pytest.fixture
def db_file(tmp_path, json_files):
    """Временная база SQLite ПР7: схема + импорт тестовых JSON."""
    path = tmp_path / "test.sqlite"
    conn = get_connection(path)
    init_db(conn)
    import_all(conn, *json_files)
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def db_conn(db_file):
    """Соединение с временной базой; строки доступны по именам."""
    conn = get_connection(db_file)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def clinic(db):
    """Тестовые данные в базе Django (те же, что в JSON выше)."""
    from animals.models import Animal
    from doctors.models import Doctor
    from visits.models import Prescription, Visit

    barsik = Animal.objects.create(
        name="Барсик", species="кошка", age=3, owner="Иванов И.И.")
    rex = Animal.objects.create(
        name="Рекс", species="собака", age=5, owner="Петрова А.С.")
    murka = Animal.objects.create(
        name="Мурка", species="кошка", age=7, owner="Смирнова Е.А.")
    sidorov = Doctor.objects.create(
        name="Сидоров П.П.", specialization="терапевт")
    kuznetsova = Doctor.objects.create(
        name="Кузнецова О.В.", specialization="хирург")
    visit1 = Visit.objects.create(
        animal=barsik, doctor=sidorov, visit_date=date(2026, 10, 15),
        diagnosis="Гастрит")
    visit2 = Visit.objects.create(
        animal=rex, doctor=sidorov, visit_date=date(2026, 10, 16),
        status=Visit.Status.CANCELLED)
    visit3 = Visit.objects.create(
        animal=murka, doctor=kuznetsova, visit_date=date(2026, 10, 15))
    Prescription.objects.create(
        visit=visit1, medication="Омепразол", dosage="1 таб.",
        duration="5 дней")
    return SimpleNamespace(
        barsik=barsik, rex=rex, murka=murka,
        sidorov=sidorov, kuznetsova=kuznetsova,
        visit1=visit1, visit2=visit2, visit3=visit3,
    )


@pytest.fixture
def future_date():
    """Функция: дата через N дней от сегодняшней."""
    from django.utils import timezone

    def _future(days=10):
        return timezone.localdate() + timedelta(days=days)

    return _future
