"""Просмотр структуры исходной базы ПР7 (только чтение).

Запуск из корня проекта: python -m db.inspect_source_db
"""
import sqlite3

from db.database import DB_PATH


def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as connection:
        connection.row_factory = sqlite3.Row
        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall()
        for (table_name,) in tables:
            print(f"\nТаблица: {table_name}")
            for column in connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ):
                print(
                    f"  имя={column['name']}, тип={column['type']}, "
                    f"NOT NULL={column['notnull']}, "
                    f"PRIMARY KEY={column['pk']}"
                )
            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]
            print(f"  записей: {count}")


if __name__ == "__main__":
    main()
