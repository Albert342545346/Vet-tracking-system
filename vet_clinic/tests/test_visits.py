from datetime import date

from models import Animal, Doctor
from models.visits import (
    create_visit,
    find_visits_by_animal,
    is_doctor_available,
)


def test_is_doctor_available():
    visits = []
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    assert is_doctor_available(visits, doctor, date(2026, 9, 25))


def test_duplicate_visit_forbidden():
    visits = []
    animal = Animal(1, "Барсик", "кошка", 3, "Иванов")
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    create_visit(visits, animal, doctor, date(2026, 9, 25))
    assert not is_doctor_available(visits, doctor, date(2026, 9, 25))


def test_cancel_visit_frees_doctor():
    visits = []
    animal = Animal(1, "Барсик", "кошка", 3, "Иванов")
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    visit = create_visit(visits, animal, doctor, date(2026, 9, 25))
    visit.cancel()
    assert is_doctor_available(visits, doctor, date(2026, 9, 25))


def test_add_prescription():
    visits = []
    animal = Animal(1, "Барсик", "кошка", 3, "Иванов")
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    visit = create_visit(visits, animal, doctor, date(2026, 9, 25))
    visit.add_prescription("Амоксициллин", "1 таб. 2 раза в день", "7 дней")
    assert len(visit.prescriptions) == 1


def test_find_visits_by_animal():
    visits = []
    cat = Animal(1, "Барсик", "кошка", 3, "Иванов")
    dog = Animal(2, "Рекс", "собака", 5, "Петров")
    doctor = Doctor(1, "Петров И.И.", "терапевт")
    create_visit(visits, cat, doctor, date(2026, 9, 25))
    create_visit(visits, dog, doctor, date(2026, 9, 26))
    create_visit(visits, cat, doctor, date(2026, 9, 27))
    assert len(find_visits_by_animal(visits, cat)) == 2
    assert len(find_visits_by_animal(visits, dog)) == 1
