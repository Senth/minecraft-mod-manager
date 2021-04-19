import os
import sqlite3
from typing import Any, List, Tuple, Union

import pytest
from minecraft_mod_manager.core.entities.repo_types import RepoTypes
from minecraft_mod_manager.core.errors.mod_already_exists import ModAlreadyExists

from ..config import config
from ..core.entities.mod import Mod
from ..gateways.sqlite import Sqlite

db_file = f".{config.app_name}.db"


@pytest.fixture
def sqlite() -> Sqlite:
    sqlite = Sqlite()
    yield sqlite
    sqlite.close()
    os.remove(db_file)


@pytest.fixture
def db() -> sqlite3.Connection:
    db = sqlite3.connect(db_file)
    yield db
    db.close()


@pytest.fixture
def cursor(db: sqlite3.Connection) -> sqlite3.Cursor:
    cursor = db.cursor()
    yield cursor
    cursor.close()


@pytest.fixture
def mod() -> Mod:
    return Mod("id", "name", "repo_id", RepoTypes.curse, "alias", upload_time=15)


def test_insert_mod(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    expected = [(mod.id, mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time, 1)]

    sqlite.insert_mod(mod)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == expected


def test_insert_mod_when_fields_set_to_none(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    mod.repo_alias = None
    mod.repo_id = None
    expected = [(mod.id, None, mod.repo_type.value, None, mod.upload_time, 1)]

    sqlite.insert_mod(mod)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == expected


def test_insert_mod_raises_error_when_already_exists(mod: Mod, sqlite: Sqlite):
    mod_duplicate = Mod("id", "name2", "repo_id2", RepoTypes.unknown, "alias2", upload_time=1)

    with pytest.raises(ModAlreadyExists) as e:
        sqlite.insert_mod(mod)
        sqlite.insert_mod(mod_duplicate)

    assert e.type == ModAlreadyExists


def test_skip_insert_mod_when_pretend(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    config.pretend = True
    sqlite.insert_mod(mod)
    cursor.execute("SELECT * FROM mod")
    config.pretend = False

    assert [] == cursor.fetchall()


def test_update_mod(mod: Mod, sqlite: Sqlite, db: sqlite3.Connection, cursor: sqlite3.Cursor):
    db.execute(
        "INSERT INTO mod (id, repo_id, repo_type, repo_alias, upload_time, active) VALUES (?, ?, ?, ?, ?, 1)",
        [mod.id, mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time],
    )
    db.commit()
    input = Mod("id", "something", "new repo id", RepoTypes.unknown, "new alias", upload_time=1337)
    expected = [("id", "new repo id", "unknown", "new alias", 1337, 1)]

    sqlite.update_mod(input)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == expected


def test_skip_update_mod_when_pretend(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    config.pretend = True
    sqlite.update_mod(mod)
    cursor.execute("SELECT * FROM mod")
    config.pretend = False

    assert [] == cursor.fetchall()


def test_insert_mod_when_calling_update_mod_but_does_not_exist(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    sqlite.update_mod(mod)
    expected = [(mod.id, mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time, 1)]

    cursor.execute("SELECT * FROM mod")

    assert expected == cursor.fetchall()


def test_exists_when_exists(mod: Mod, sqlite: Sqlite, db: sqlite3.Connection):
    db.execute(
        "INSERT INTO mod (id, repo_id, repo_type, repo_alias, upload_time, active) VALUES (?, ?, ?, ?, ?, 1)",
        [mod.id, mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time],
    )
    db.commit()

    result = sqlite.exists(mod.id)

    assert result


def test_exists_when_doesnt_exists(sqlite: Sqlite):
    result = sqlite.exists("id")

    assert not result


class SyncWithDirTest:
    def __init__(
        self,
        name: str,
        db_before: List[Tuple[str, Union[str, None], str, Union[str, None], int, int]] = [],
        input: List[Mod] = [],
        expected: List[Mod] = [],
        db_after: List[Any] = [],
    ) -> None:
        self.name = name
        self.db_before = db_before
        self.input = input
        self.expected = expected
        self.db_after = db_after


def row(
    id: str, repo_id: Union[str, None] = None, repo="unknown", alias: Union[str, None] = None, upload_time=0, active=1
) -> Tuple[str, Union[str, None], str, Union[str, None], int, int]:
    return (id, repo_id, repo, alias, upload_time, active)


@pytest.mark.parametrize(
    "test",
    [
        SyncWithDirTest(
            name="First time, add all mods",
            input=[
                Mod("1", "name1", repo_id="123"),
                Mod("2", "name2", repo_type=RepoTypes.curse),
            ],
            expected=[
                Mod("1", "name1", repo_id="123"),
                Mod("2", "name2", repo_type=RepoTypes.curse),
            ],
            db_after=[
                row("1", repo_id="123"),
                row("2", repo="curse"),
            ],
        ),
        SyncWithDirTest(
            name="Remove one mod",
            db_before=[
                row("1", repo_id="125"),
                row("2", repo="curse"),
            ],
            input=[
                Mod("1", "name1"),
            ],
            expected=[
                Mod("1", "name1"),
            ],
            db_after=[
                row("1", repo_id="125"),
                row("2", repo="curse", active=0),
            ],
        ),
        SyncWithDirTest(
            name="Remove and add mod",
            db_before=[
                row(
                    "1",
                ),
                row("2", repo="curse"),
            ],
            input=[
                Mod("1", "name1"),
                Mod("3", "name3"),
            ],
            expected=[
                Mod("1", "name1"),
                Mod("3", "name3"),
            ],
            db_after=[
                row("1"),
                row("2", repo="curse", active=0),
                row("3"),
            ],
        ),
        SyncWithDirTest(
            name="Get existing info from mods",
            db_before=[
                row("1", alias="alias", upload_time=1337),
                row("2", repo="curse"),
            ],
            input=[
                Mod("1", "name1"),
                Mod("2", "name2"),
            ],
            expected=[
                Mod("1", "name1", repo_alias="alias", upload_time=1337),
                Mod("2", "name2", repo_type=RepoTypes.curse),
            ],
            db_after=[
                row("1", alias="alias", upload_time=1337),
                row("2", repo="curse"),
            ],
        ),
        SyncWithDirTest(
            name="Get existing info from old info",
            db_before=[
                row("1", alias="alias", upload_time=1337, active=0),
                row("2", repo="curse", active=0),
            ],
            input=[
                Mod("1", "name1"),
                Mod("2", "name2"),
            ],
            expected=[
                Mod("1", "name1", repo_alias="alias", upload_time=1337),
                Mod("2", "name2", repo_type=RepoTypes.curse),
            ],
            db_after=[
                row("1", alias="alias", upload_time=1337),
                row("2", repo="curse"),
            ],
        ),
    ],
)
def test_sync_with_dir(test: SyncWithDirTest, sqlite: Sqlite, db: sqlite3.Connection, cursor: sqlite3.Cursor):
    print(f"Test: {test.name}")

    # Insert initial data
    for row in test.db_before:
        db.execute(
            "INSERT INTO mod (id, repo_id, repo_type, repo_alias, upload_time, active) VALUES (?, ?, ?, ?, ?, ?)",
            list(row),
        )
    db.commit()

    # Sync with dir
    result = sqlite.sync_with_dir(test.input)

    assert result == test.expected

    # Test DB after sync
    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == test.db_after
