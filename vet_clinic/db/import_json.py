"""Однократный перенос данных из JSON-файлов в SQLite (ПР7).

Запуск из корня проекта:
    python -m db.import_json            # импорт в пустую базу
    python -m db.import_json --force    # очистить таблицы и импортировать
"""
import json
import sys

from db.database import BASE_DIR, get_connection, init_db

DATA_DIR = BASE_DIR / "data"
ANIMALS_FILE = DATA_DIR / "animals.json"
DOCTORS_FILE = DATA_DIR / "doctors.json"
VISITS_FILE = DATA_DIR / "visits.json"


def load_json(filename):
    """Прочитать список записей из JSON-файла."""
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_animals(conn, filename=ANIMALS_FILE):
    """Перенести животных в таблицу animals."""
    animals = load_json(filename)
    conn.executemany(
        """
        INSERT INTO animals (
            id,
            name,
            species,
            age,
            owner
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                animal["id"],
                animal["name"],
                animal["species"],
                animal["age"],
                animal["owner"],
            )
            for animal in animals
        ],
    )


def import_doctors(conn, filename=DOCTORS_FILE):
    """Перенести врачей в таблицу doctors."""
    doctors = load_json(filename)
    conn.executemany(
        """
        INSERT INTO doctors (
            id,
            name,
            specialization
        )
        VALUES (?, ?, ?)
        """,
        [
            (
                doctor["id"],
                doctor["name"],
                doctor["specialization"],
            )
            for doctor in doctors
        ],
    )


def import_visits(conn, filename=VISITS_FILE):
    """Перенести посещения (visits) и их назначения (prescriptions).

    Посещения ссылаются на животных и врачей, поэтому импортируются
    после них. Пустой диагноз сохраняется как NULL.
    """
    visits = load_json(filename)
    conn.executemany(
        """
        INSERT INTO visits (
            id,
            animal_id,
            doctor_id,
            visit_date,
            diagnosis,
            is_cancelled
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                visit["id"],
                visit["animal_id"],
                visit["doctor_id"],
                visit["date"],
                visit["diagnosis"] or None,
                int(visit["is_cancelled"]),
            )
            for visit in visits
        ],
    )
    conn.executemany(
        """
        INSERT INTO prescriptions (
            visit_id,
            medication,
            dosage,
            duration
        )
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                visit["id"],
                prescription["medication"],
                prescription["dosage"],
                prescription["duration"],
            )
            for visit in visits
            for prescription in visit["prescriptions"]
        ],
    )


def import_all(
    conn,
    animals_file=ANIMALS_FILE,
    doctors_file=DOCTORS_FILE,
    visits_file=VISITS_FILE,
):
    """Импортировать все данные в правильном порядке (из-за FOREIGN KEY)."""
    import_animals(conn, animals_file)
    import_doctors(conn, doctors_file)
    import_visits(conn, visits_file)


def clear_tables(conn):
    """Очистить таблицы: сначала зависимые, затем родительские."""
    conn.execute("DELETE FROM prescriptions")
    conn.execute("DELETE FROM visits")
    conn.execute("DELETE FROM animals")
    conn.execute("DELETE FROM doctors")


def has_data(conn):
    """Проверить, есть ли уже данные в базе."""
    return conn.execute("SELECT COUNT(*) FROM animals").fetchone()[0] > 0


def main(argv=None):
    """Создать таблицы (если нужно) и перенести данные из JSON."""
    args = sys.argv[1:] if argv is None else argv
    force = "--force" in args
    conn = get_connection()
    try:
        init_db(conn)
        if has_data(conn) and not force:
            print(
                "В базе уже есть данные, импорт пропущен. "
                "Для повторного импорта: python -m db.import_json --force"
            )
            return
        if force:
            clear_tables(conn)
        import_all(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    print("Данные из JSON перенесены в SQLite.")


if __name__ == "__main__":
    main()
