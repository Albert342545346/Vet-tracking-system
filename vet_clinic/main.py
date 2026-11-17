"""Точка входа в приложение «Система учета ветеринарных посещений»."""

from models.animals import (
    add_animal,
    find_animal,
    find_animal_by_id,
    show_animals,
)
from models.doctors import add_doctor, find_doctor_by_id, show_doctors
from models.visits import (
    cancel_visit,
    create_visit,
    find_visit_by_id,
    show_visits,
)
from storage import (
    load_animals,
    load_doctors,
    load_visits,
    save_animals,
    save_doctors,
    save_visits,
)
from utils import input_date, input_int

ANIMALS_FILE = "data/animals.json"
DOCTORS_FILE = "data/doctors.json"
VISITS_FILE = "data/visits.json"

MENU = """
=== Система учета ветеринарных посещений ===
1. Показать животных
2. Добавить животное
3. Найти животное
4. Показать врачей
5. Добавить врача
6. Записать на посещение
7. Показать посещения
8. Отменить посещение
9. Добавить назначение к посещению
0. Выход
"""


def create_new_visit(visits: list, animals: list, doctors: list) -> None:
    """Пользовательский сценарий записи животного на посещение."""
    animal_id = input_int("ID животного: ")
    animal = find_animal_by_id(animals, animal_id)
    if animal is None:
        print("Животное не найдено.")
        return
    doctor_id = input_int("ID врача: ")
    doctor = find_doctor_by_id(doctors, doctor_id)
    if doctor is None:
        print("Врач не найден.")
        return
    visit_date = input_date("Дата посещения (ГГГГ-ММ-ДД): ")
    visit = create_visit(visits, animal, doctor, visit_date)
    if visit is None:
        print("Врач занят на указанную дату.")
        return
    print(f"Посещение создано, id = {visit.id}")


def add_new_prescription(visits: list) -> None:
    """Пользовательский сценарий добавления диагноза и назначения."""
    visit_id = input_int("ID посещения: ")
    visit = find_visit_by_id(visits, visit_id)
    if visit is None:
        print("Посещение не найдено.")
        return
    diagnosis = input("Диагноз (можно оставить пустым): ")
    if diagnosis:
        visit.set_diagnosis(diagnosis)
    medication = input("Препарат: ")
    dosage = input("Дозировка: ")
    duration = input("Длительность приема: ")
    visit.add_prescription(medication, dosage, duration)
    print("Назначение добавлено.")


def main() -> None:
    """Точка запуска приложения."""
    animals = load_animals(ANIMALS_FILE)
    doctors = load_doctors(DOCTORS_FILE)
    visits = load_visits(VISITS_FILE, animals, doctors)

    while True:
        print(MENU)
        choice = input("Выберите действие: ")

        if choice == "1":
            show_animals(animals)
        elif choice == "2":
            name = input("Кличка: ")
            species = input("Вид: ")
            age = input_int("Возраст: ")
            owner = input("Владелец: ")
            add_animal(animals, name, species, age, owner)
        elif choice == "3":
            query = input("Подстрока клички: ")
            show_animals(find_animal(animals, query))
        elif choice == "4":
            show_doctors(doctors)
        elif choice == "5":
            name = input("ФИО врача: ")
            specialization = input("Специализация: ")
            add_doctor(doctors, name, specialization)
        elif choice == "6":
            create_new_visit(visits, animals, doctors)
        elif choice == "7":
            show_visits(visits)
        elif choice == "8":
            visit_id = input_int("ID посещения: ")
            if cancel_visit(visits, visit_id):
                print("Посещение отменено.")
            else:
                print("Посещение не найдено.")
        elif choice == "9":
            add_new_prescription(visits)
        elif choice == "0":
            save_animals(ANIMALS_FILE, animals)
            save_doctors(DOCTORS_FILE, doctors)
            save_visits(VISITS_FILE, visits)
            print("Данные сохранены. До свидания!")
            break
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()
