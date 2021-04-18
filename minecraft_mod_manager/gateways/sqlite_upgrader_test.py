import os
import sqlite3

import pytest

from ..config import config
from .sqlite import Sqlite

db_file = f".{config.app_name}.db"


@pytest.fixture
def db() -> sqlite3.Connection:
    db = sqlite3.connect(db_file)
    yield db
    db.close()
    os.remove(db_file)


@pytest.fixture
def cursor(db: sqlite3.Connection) -> sqlite3.Cursor:
    cursor = db.cursor()
    yield cursor
    cursor.close()


def test_create_tables_on_first_run(cursor: sqlite3.Cursor):
    sqlite = Sqlite()
    sqlite.close()

    cursor.execute("SELECT * FROM mod")
    mods = cursor.fetchall()
    assert mods == []

    cursor.execute("SELECT * FROM version")
    version = cursor.fetchall()
    assert version == [(1,)]


def test_v0_to_v1(db: sqlite3.Connection, cursor: sqlite3.Cursor):
    db.execute(
        "CREATE TABLE mod ("
        + "id TEXT UNIQUE, "
        + "repo_type TEXT, "
        + "repo_name TEXT, "
        + "upload_time INTEGER, "
        + "active INTEGER)"
    )
    db.execute(
        "INSERT INTO mod (id, repo_type, repo_name, upload_time, active) VALUES "
        + "('carpet', 'curse', 'carpet', 1, 1)"
    )
    db.commit()

    sqlite = Sqlite()
    sqlite.close()

    cursor.execute("SELECT * FROM mod")
    mods = cursor.fetchall()
    assert mods == []

    cursor.execute("SELECT * FROM version")
    version = cursor.fetchall()
    assert version == [(1,)]
