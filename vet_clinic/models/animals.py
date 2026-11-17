"""Класс Animal и функции для работы с коллекцией животных."""

from typing import List, Optional


class Animal:
    """Животное, состоящее на учете в клинике."""

    def __init__(
        self,
        animal_id: int,
        name: str,
        species: str,
        age: int,
        owner: str,
    ) -> None:
        """Создать объект животного."""
        self.id = animal_id
        self.name = name
        self.species = species
        self.age = age
        self.owner = owner

    def is_species(self, species: str) -> bool:
        """Проверить принадлежность животного к указанному виду."""
        return self.species.lower() == species.lower()

    @classmethod
    def from_data(cls, data: dict) -> "Animal":
        """Создать животное из словаря данных (например, из JSON)."""
        return cls(
            animal_id=data["id"],
            name=data["name"],
            species=data["species"],
            age=data["age"],
            owner=data["owner"],
        )

    def to_data(self) -> dict:
        """Преобразовать объект в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "owner": self.owner,
        }

    def __str__(self) -> str:
        """Вернуть строковое представление животного."""
        return (
            f"{self.name} ({self.species}, {self.age} лет), "
            f"владелец: {self.owner}"
        )


def add_animal(
    animals: List[Animal],
    name: str,
    species: str,
    age: int,
    owner: str,
) -> Animal:
    """Создать объект Animal и добавить его в коллекцию."""
    new_id = max((a.id for a in animals), default=0) + 1
    animal = Animal(new_id, name, species, age, owner)
    animals.append(animal)
    return animal


def find_animal(animals: List[Animal], query: str) -> List[Animal]:
    """Найти животных по подстроке клички."""
    query = query.lower()
    return [a for a in animals if query in a.name.lower()]


def find_animal_by_id(
    animals: List[Animal], animal_id: int
) -> Optional[Animal]:
    """Найти животное по идентификатору."""
    for animal in animals:
        if animal.id == animal_id:
            return animal
    return None


def filter_animals_by_species(
    animals: List[Animal], species: str
) -> List[Animal]:
    """Отобрать животных заданного вида."""
    return [a for a in animals if a.is_species(species)]


def sort_animals_by_age(animals: List[Animal]) -> List[Animal]:
    """Вернуть животных, отсортированных по возрасту."""
    return sorted(animals, key=lambda a: a.age)


def show_animals(animals: List[Animal]) -> None:
    """Вывести список животных."""
    if not animals:
        print("Список животных пуст.")
        return
    for animal in animals:
        print(f"[{animal.id}] {animal}")
