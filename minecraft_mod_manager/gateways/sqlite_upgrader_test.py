import os
import sqlite3

import pytest
from minecraft_mod_manager.gateways.sqlite_upgrader import SqliteUpgrader

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

    assert_version(cursor)


def test_v0_to_v1(db: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute(
        "CREATE TABLE mod ("
        + "id TEXT UNIQUE, "
        + "repo_type TEXT, "
        + "repo_name TEXT, "
        + "upload_time INTEGER, "
        + "active INTEGER)"
    )
    cursor.execute(
        "INSERT INTO mod (id, repo_type, repo_name, upload_time, active) VALUES "
        + "('carpet', 'curse', 'carpet', 1, 1)"
    )
    db.commit()

    upgrader = SqliteUpgrader(db, cursor)
    upgrader._v0_to_v1()

    cursor.execute("SELECT * FROM mod")
    mods = cursor.fetchall()
    assert [] == mods

    assert_version(cursor)


@pytest.mark.parametrize(
    "test_name,input,expected",
    [
        (
            "Migrates all fields when present",
            ("id", "curse", "site_id", "site_slug", 123, 1),
            ("id", "curse:site_id:site_slug", 123, 1),
        ),
        (
            "Skip saving slug when no site is specified",
            ("id", "", "", "slug", 123, 1),
            ("id", "", 123, 1),
        ),
        (
            "Migrate slug when no site_id",
            ("id", "curse", "", "site_slug", 123, 0),
            ("id", "curse::site_slug", 123, 0),
        ),
        (
            "Skip when site is unknown",
            ("id", "unknown", "", "", 123, 1),
            ("id", "", 123, 1),
        ),
        (
            "Convert 'None' to empty",
            ("id", "curse", "None", "None", 123, 1),
            ("id", "curse::", 123, 1),
        ),
    ],
)
def test_v1_to_v2(test_name: str, input, expected, db: sqlite3.Connection, cursor: sqlite3.Cursor):
    print(test_name)

    cursor.execute(
        "CREATE TABLE mod ("
        + "id TEXT UNIQUE, "
        + "site TEXT, "
        + "site_id TEXT, "
        + "site_slug TEXT, "
        + "upload_time INTEGER, "
        + "active INTEGER)"
    )
    cursor.execute(
        "INSERT INTO mod (id, site, site_id, site_slug, upload_time, active) VALUES (?, ?, ?, ?, ?, ?)", input
    )
    db.commit()

    upgrader = SqliteUpgrader(db, cursor)
    upgrader._v1_to_v2()

    cursor.execute("SELECT * FROM mod")
    result = cursor.fetchall()

    assert [expected] == result


def create_version_table(version: int, db: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
    cursor.execute("CREATE TABLE version (version INTEGER)")
    cursor.execute("INSERT INTO version (version) VALUES(?)", (version,))


def assert_version(cursor: sqlite3.Cursor) -> None:
    cursor.execute("SELECT * FROM version")
    versions = cursor.fetchall()
    assert [(SqliteUpgrader._version,)] == versions
