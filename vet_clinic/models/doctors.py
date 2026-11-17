"""Класс Doctor и функции для работы с коллекцией врачей."""

from typing import List, Optional


class Doctor:
    """Ветеринарный врач клиники."""

    def __init__(self, doctor_id: int, name: str, specialization: str) -> None:
        """Создать объект врача."""
        self.id = doctor_id
        self.name = name
        self.specialization = specialization

    @classmethod
    def from_data(cls, data: dict) -> "Doctor":
        """Создать врача из словаря данных (например, из JSON)."""
        return cls(
            doctor_id=data["id"],
            name=data["name"],
            specialization=data["specialization"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление врача."""
        return f"{self.name} — {self.specialization}"


def add_doctor(
    doctors: List[Doctor], name: str, specialization: str
) -> Doctor:
    """Создать объект Doctor и добавить его в коллекцию."""
    new_id = max((d.id for d in doctors), default=0) + 1
    doctor = Doctor(new_id, name, specialization)
    doctors.append(doctor)
    return doctor


def find_doctor(doctors: List[Doctor], query: str) -> List[Doctor]:
    """Найти врачей по подстроке ФИО или специализации."""
    query = query.lower()
    return [
        d for d in doctors
        if query in d.name.lower() or query in d.specialization.lower()
    ]


def find_doctor_by_id(
    doctors: List[Doctor], doctor_id: int
) -> Optional[Doctor]:
    """Найти врача по идентификатору."""
    for doctor in doctors:
        if doctor.id == doctor_id:
            return doctor
    return None


def show_doctors(doctors: List[Doctor]) -> None:
    """Вывести список врачей."""
    if not doctors:
        print("Список врачей пуст.")
        return
    for doctor in doctors:
        print(f"[{doctor.id}] {doctor}")
