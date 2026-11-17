from models import Animal
from models.animals import add_animal, filter_animals_by_species, find_animal


def test_animal_creation():
    animal = Animal(1, "Барсик", "кошка", 3, "Иванов")
    assert animal.id == 1
    assert animal.name == "Барсик"
    assert animal.species == "кошка"


def test_add_animal():
    animals = []
    add_animal(animals, "Барсик", "кошка", 3, "Иванов")
    assert len(animals) == 1


def test_find_animal():
    animals = []
    add_animal(animals, "Барсик", "кошка", 3, "Иванов")
    assert find_animal(animals, "барс")


def test_filter_animals_by_species():
    animals = []
    add_animal(animals, "Барсик", "кошка", 3, "Иванов")
    add_animal(animals, "Рекс", "собака", 5, "Петров")
    result = filter_animals_by_species(animals, "кошка")
    assert len(result) == 1
