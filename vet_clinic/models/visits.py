"""Классы Visit и Prescription, функции работы с посещениями."""

from datetime import date
from typing import List, Optional

from .animals import Animal
from .doctors import Doctor


class Prescription:
    """Назначение (лечение), выданное в рамках посещения."""

    def __init__(self, medication: str, dosage: str, duration: str) -> None:
        """Создать объект назначения."""
        self.medication = medication
        self.dosage = dosage
        self.duration = duration

    @classmethod
    def from_data(cls, data: dict) -> "Prescription":
        """Создать назначение из словаря данных."""
        return cls(
            medication=data["medication"],
            dosage=data["dosage"],
            duration=data["duration"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "medication": self.medication,
            "dosage": self.dosage,
            "duration": self.duration,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление назначения."""
        return f"{self.medication}, {self.dosage}, {self.duration}"


class Visit:
    """Посещение ветеринарной клиники."""

    def __init__(
        self,
        visit_id: int,
        animal: Animal,
        doctor: Doctor,
        visit_date: str,
        diagnosis: str = "",
        is_cancelled: bool = False,
    ) -> None:
        """Создать объект посещения."""
        self.id = visit_id
        self.animal = animal
        self.doctor = doctor
        self.visit_date = visit_date
        self.diagnosis = diagnosis
        self.is_cancelled = is_cancelled
        self.prescriptions: List[Prescription] = []

    def cancel(self) -> None:
        """Отменить посещение (не удаляя его из коллекции)."""
        self.is_cancelled = True

    def set_diagnosis(self, diagnosis: str) -> None:
        """Установить диагноз по итогам посещения."""
        self.diagnosis = diagnosis

    def add_prescription(
        self, medication: str, dosage: str, duration: str
    ) -> Prescription:
        """Добавить назначение к посещению."""
        prescription = Prescription(medication, dosage, duration)
        self.prescriptions.append(prescription)
        return prescription

    def __str__(self) -> str:
        """Вернуть строковое представление посещения с учетом статуса."""
        status = "отменено" if self.is_cancelled else "активно"
        return (
            f"{self.animal.name} у врача {self.doctor.name}, "
            f"{self.visit_date}, диагноз: {self.diagnosis or '—'}, "
            f"статус: {status}"
        )


def is_doctor_available(
    visits: List[Visit], doctor: Doctor, visit_date: date
) -> bool:
    """Проверить, свободен ли врач на указанную дату."""
    for visit in visits:
        same_doctor = visit.doctor.id == doctor.id
        same_date = visit.visit_date == visit_date.isoformat()
        if same_doctor and same_date and not visit.is_cancelled:
            return False
    return True


def create_visit(
    visits: List[Visit],
    animal: Animal,
    doctor: Doctor,
    visit_date: date,
) -> Optional[Visit]:
    """Создать объект Visit, если врач свободен на указанную дату."""
    if not is_doctor_available(visits, doctor, visit_date):
        return None
    new_id = max((v.id for v in visits), default=0) + 1
    visit = Visit(new_id, animal, doctor, visit_date.isoformat())
    visits.append(visit)
    return visit


def find_visit_by_id(visits: List[Visit], visit_id: int) -> Optional[Visit]:
    """Найти посещение по идентификатору."""
    for visit in visits:
        if visit.id == visit_id:
            return visit
    return None


def find_visits_by_animal(
    visits: List[Visit], animal: Animal
) -> List[Visit]:
    """Вернуть историю посещений животного (включая отмененные)."""
    return [v for v in visits if v.animal.id == animal.id]


def cancel_visit(visits: List[Visit], visit_id: int) -> bool:
    """Найти посещение по идентификатору и отменить его через его метод."""
    visit = find_visit_by_id(visits, visit_id)
    if visit is None:
        return False
    visit.cancel()
    return True


def get_visit_status(is_cancelled: bool) -> str:
    """Вернуть текстовый статус посещения (функция из ПР1/ПР2)."""
    if is_cancelled:
        return "Посещение отменено"
    return "Посещение активно"


def show_visits(visits: List[Visit]) -> None:
    """Вывести список посещений вместе с назначениями."""
    if not visits:
        print("Список посещений пуст.")
        return
    for visit in visits:
        print(f"[{visit.id}] {visit}")
        for prescription in visit.prescriptions:
            print(f"    назначение: {prescription}")
