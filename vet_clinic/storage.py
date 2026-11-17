"""Загрузка и сохранение объектов проекта в формате JSON."""

import json
from typing import List

from models import Animal, Doctor
from models.animals import find_animal_by_id
from models.doctors import find_doctor_by_id
from models.visits import Prescription, Visit


def _read_json(filename: str) -> list:
    """Прочитать список записей из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(
            f"Предупреждение: файл {filename} поврежден, "
            "используется пустой список."
        )
        return []


def _write_json(filename: str, data: list) -> None:
    """Записать список записей в JSON-файл."""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_animals(filename: str) -> List[Animal]:
    """Загрузить животных из JSON-файла и создать объекты Animal."""
    return [Animal.from_data(item) for item in _read_json(filename)]


def save_animals(filename: str, animals: List[Animal]) -> None:
    """Сохранить объекты Animal в JSON-файл."""
    _write_json(filename, [animal.to_data() for animal in animals])


def load_doctors(filename: str) -> List[Doctor]:
    """Загрузить врачей из JSON-файла и создать объекты Doctor."""
    return [Doctor.from_data(item) for item in _read_json(filename)]


def save_doctors(filename: str, doctors: List[Doctor]) -> None:
    """Сохранить объекты Doctor в JSON-файл."""
    _write_json(filename, [doctor.to_data() for doctor in doctors])


def load_visits(
    filename: str, animals: List[Animal], doctors: List[Doctor]
) -> List[Visit]:
    """Загрузить посещения из JSON, восстановив связи с Animal и Doctor."""
    visits: List[Visit] = []
    for item in _read_json(filename):
        animal = find_animal_by_id(animals, item["animal_id"])
        doctor = find_doctor_by_id(doctors, item["doctor_id"])
        if animal is None or doctor is None:
            continue
        visit = Visit(
            visit_id=item["id"],
            animal=animal,
            doctor=doctor,
            visit_date=item["date"],
            diagnosis=item["diagnosis"],
            is_cancelled=item["is_cancelled"],
        )
        visit.prescriptions = [
            Prescription.from_data(p) for p in item["prescriptions"]
        ]
        visits.append(visit)
    return visits


def save_visits(filename: str, visits: List[Visit]) -> None:
    """Сохранить объекты Visit в JSON (по id связанных объектов)."""
    data = [
        {
            "id": visit.id,
            "animal_id": visit.animal.id,
            "doctor_id": visit.doctor.id,
            "date": visit.visit_date,
            "diagnosis": visit.diagnosis,
            "is_cancelled": visit.is_cancelled,
            "prescriptions": [p.to_data() for p in visit.prescriptions],
        }
        for visit in visits
    ]
    _write_json(filename, data)
