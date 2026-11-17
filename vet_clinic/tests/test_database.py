"""Тесты слоя базы данных: схема, ключи, импорт, файл queries.sql."""
import sqlite3
from pathlib import Path

import pytest

from db.database import BASE_DIR, create_database, get_connection, init_db
from db.import_json import clear_tables, has_data, import_all

QUERIES_FILE = Path(BASE_DIR) / "sql" / "queries.sql"


def count(conn, table):
    """Вернуть число записей в таблице (имя таблицы задано в тестах)."""
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def read_statements(path):
    """Разобрать SQL-файл на отдельные запросы."""
    statements = []
    buffer = ""
    for line in path.read_text(encoding="utf-8").splitlines(keepends=True):
        buffer += line
        if sqlite3.complete_statement(buffer):
            statements.append(buffer.strip())
            buffer = ""
    return statements


def test_schema_creates_tables(tmp_path):
    path = create_database(tmp_path / "new.sqlite")
    conn = sqlite3.connect(path)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    conn.close()
    assert {"animals", "doctors", "visits", "prescriptions"} <= tables


def test_schema_can_be_applied_twice(tmp_path):
    conn = get_connection(tmp_path / "twice.sqlite")
    init_db(conn)
    init_db(conn)
    conn.close()


def test_foreign_keys_declared(db_conn):
    rows = db_conn.execute("PRAGMA foreign_key_list(visits)").fetchall()
    assert {row["table"] for row in rows} == {"animals", "doctors"}


def test_foreign_keys_are_enforced(db_conn):
    with pytest.raises(sqlite3.IntegrityError):
        db_conn.execute(
            "INSERT INTO visits (animal_id, doctor_id, visit_date) "
            "VALUES (?, ?, ?)",
            [999, 1, "2026-12-01"],
        )


def test_import_counts(db_conn):
    assert count(db_conn, "animals") == 3
    assert count(db_conn, "doctors") == 2
    assert count(db_conn, "visits") == 3
    assert count(db_conn, "prescriptions") == 1


def test_import_converts_values(db_conn):
    visit = db_conn.execute(
        "SELECT diagnosis, is_cancelled FROM visits WHERE id = 2"
    ).fetchone()
    assert visit["diagnosis"] is None
    assert visit["is_cancelled"] == 1


def test_import_keeps_prescription_link(db_conn):
    row = db_conn.execute(
        "SELECT visit_id, medication FROM prescriptions"
    ).fetchone()
    assert (row["visit_id"], row["medication"]) == (1, "Омепразол")


def test_has_data_and_clear_tables(db_conn):
    assert has_data(db_conn)
    clear_tables(db_conn)
    assert not has_data(db_conn)


def test_import_twice_fails_and_rolls_back(db_conn, json_files):
    with pytest.raises(sqlite3.IntegrityError):
        import_all(db_conn, *json_files)
    db_conn.rollback()
    assert count(db_conn, "animals") == 3


def test_queries_file_executes(db_conn):
    statements = read_statements(QUERIES_FILE)
    assert len(statements) >= 10
    for statement in statements:
        db_conn.execute(statement).fetchall()


def test_queries_file_covers_required_kinds():
    text = QUERIES_FILE.read_text(encoding="utf-8").upper()
    statements = read_statements(QUERIES_FILE)
    assert len(statements) >= 10
    for keyword in ("WHERE", "JOIN", "COUNT(", "GROUP BY", "HAVING"):
        assert text.count(keyword) >= 2, keyword


def test_py_lower_handles_cyrillic(db_conn):
    row = db_conn.execute("SELECT py_lower('БАРСИК') AS value").fetchone()
    assert row["value"] == "барсик"
