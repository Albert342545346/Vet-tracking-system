"""Подключение к базе данных SQLite проекта VetClinic (ПР7)."""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "vetclinic.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def _py_lower(value):
    """Привести строку к нижнему регистру.

    Встроенная функция LOWER() в SQLite понимает только латиницу,
    поэтому для регистронезависимого поиска по кириллице
    регистрируется собственная функция py_lower().
    """
    if isinstance(value, str):
        return value.lower()
    return value


def get_connection(db_path=None):
    """Создать соединение с базой данных и настроить его.

    PRAGMA foreign_keys = ON включает проверку внешних ключей для
    текущего соединения (по умолчанию SQLite их не контролирует).
    """
    conn = sqlite3.connect(DB_PATH if db_path is None else db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("py_lower", 1, _py_lower, deterministic=True)
    return conn


def init_db(conn):
    """Создать таблицы, выполнив sql/schema.sql.

    Скрипт содержит IF NOT EXISTS, поэтому повторный запуск безопасен.
    """
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(script)
    conn.commit()


def create_database(db_path=None):
    """Создать файл базы данных и таблицы; вернуть путь к файлу."""
    path = Path(DB_PATH if db_path is None else db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(path)
    try:
        init_db(conn)
    finally:
        conn.close()
    return path


if __name__ == "__main__":
    print(f"База данных создана: {create_database()}")
