import os
import sqlite3
from typing import Any, Dict, List, Tuple, Union

import pytest

from ..config import config
from ..core.entities.mod import Mod
from ..core.entities.sites import Site, Sites
from ..core.errors.mod_already_exists import ModAlreadyExists
from ..gateways.sqlite import Sqlite, _Column

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
    return Mod("id", "name", sites={Sites.curse: Site(Sites.curse, "id", "slug")}, upload_time=123)


def test_insert_mod(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    expected = [
        row(
            id=mod.id,
            sites="curse:id:slug",
            upload_time=mod.upload_time,
            active=1,
        )
    ]

    sqlite.insert_mod(mod)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == expected


def test_insert_mod_when_fields_set_to_none(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    expected = [
        row(
            id=mod.id,
            sites="curse:id:slug",
            upload_time=mod.upload_time,
            active=1,
        )
    ]

    sqlite.insert_mod(mod)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == expected


def test_insert_mod_raises_error_when_already_exists(mod: Mod, sqlite: Sqlite):
    mod_duplicate = Mod("id", "name2", upload_time=1)

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
        "INSERT INTO mod (id, sites, upload_time, active) VALUES (?, ?, ?, 1)",
        ["id", "", 123],
    )
    db.commit()
    input = mod
    expected = [("id", "curse:id:slug", 123, 1)]

    sqlite.update_mod(input)

    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert expected == rows


def test_skip_update_mod_when_pretend(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    config.pretend = True
    sqlite.update_mod(mod)
    cursor.execute("SELECT * FROM mod")
    config.pretend = False

    assert [] == cursor.fetchall()


def test_insert_mod_when_calling_update_mod_but_does_not_exist(mod: Mod, sqlite: Sqlite, cursor: sqlite3.Cursor):
    sqlite.update_mod(mod)
    expected = [row(mod.id, mod.sites, mod.upload_time, 1)]

    cursor.execute("SELECT * FROM mod")

    assert expected == cursor.fetchall()


@pytest.mark.parametrize(
    "name,row,filter,expected",
    [
        (
            "Exists when exists",
            ("id", "", 123, 1),
            True,
            True,
        ),
        (
            "Does not exist when inactive",
            ("id", "", 123, 0),
            True,
            False,
        ),
        (
            "Exists when inactive but filter is inactive",
            ("id", "", 123, 0),
            False,
            True,
        ),
        (
            "Does not exist when it does not exist",
            ("invalid", "", 123, 0),
            False,
            False,
        ),
    ],
)
def test_exists(name, row, filter, expected, sqlite: Sqlite, cursor: sqlite3.Cursor):
    print(name)
    cursor.execute("INSERT INTO mod (id, sites, upload_time, active) VALUES (?, ?, ?, ?)", row)
    cursor.connection.commit()

    result = sqlite.exists("id", filter)
    assert expected == result


class SyncWithDirTest:
    def __init__(
        self,
        name: str,
        db_before: List[Tuple[str, str, int, int]] = [],
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
    id: str, sites: Union[str, Dict[Sites, Site], None] = "", upload_time=0, active=1
) -> Tuple[str, str, int, int]:
    if isinstance(sites, dict):
        sites = _Column.dict_sites_to_string(sites)
    elif sites is None:
        sites = ""
    return (id, sites, upload_time, active)


@pytest.mark.parametrize(
    "test",
    [
        SyncWithDirTest(
            name="First time, add all mods",
            input=[
                Mod("1", "name1", {Sites.curse: Site(Sites.curse, "123", "slug")}),
                Mod("2", "name2"),
            ],
            expected=[
                Mod("1", "name1", {Sites.curse: Site(Sites.curse, "123", "slug")}),
                Mod("2", "name2"),
            ],
            db_after=[
                row("1", "curse:123:slug"),
                row("2"),
            ],
        ),
        SyncWithDirTest(
            name="Remove one mod",
            db_before=[
                row("1"),
                row("2"),
            ],
            input=[
                Mod("1", "name1"),
            ],
            expected=[
                Mod("1", "name1"),
            ],
            db_after=[
                row("1"),
                row("2", active=0),
            ],
        ),
        SyncWithDirTest(
            name="Reactivate one mod",
            db_before=[
                row("1"),
                row("2", active=0),
            ],
            input=[
                Mod("1", ""),
                Mod("2", ""),
            ],
            expected=[
                Mod("1", ""),
                Mod("2", ""),
            ],
            db_after=[
                row("1"),
                row("2"),
            ],
        ),
        SyncWithDirTest(
            name="Remove and add mod",
            db_before=[
                row("1"),
                row("2"),
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
                row("2", active=0),
                row("3"),
            ],
        ),
        SyncWithDirTest(
            name="Get existing info from mods",
            db_before=[
                row("1", sites="curse:id:slug", upload_time=1337),
                row("2", sites="curse::"),
            ],
            input=[
                Mod("1", "name1"),
                Mod("2", "name2"),
            ],
            expected=[
                Mod("1", "name1", {Sites.curse: Site(Sites.curse, "id", "slug")}, upload_time=1337),
                Mod("2", "name2", {Sites.curse: Site(Sites.curse)}),
            ],
            db_after=[
                row("1", sites="curse:id:slug", upload_time=1337),
                row("2", sites="curse::"),
            ],
        ),
        SyncWithDirTest(
            name="Get existing info from old info",
            db_before=[
                row("1", sites="curse:id:slug", upload_time=1337, active=0),
                row("2", sites="curse::", active=0),
            ],
            input=[
                Mod("1", "name1"),
                Mod("2", "name2"),
            ],
            expected=[
                Mod("1", "name1", {Sites.curse: Site(Sites.curse, "id", "slug")}, upload_time=1337),
                Mod("2", "name2", {Sites.curse: Site(Sites.curse)}),
            ],
            db_after=[
                row("1", sites="curse:id:slug", upload_time=1337),
                row("2", sites="curse::"),
            ],
        ),
        SyncWithDirTest(
            name="Replace dict when specified",
            db_before=[
                row("1", sites="curse:id:slug", upload_time=1337),
                row("2", sites="curse::"),
            ],
            input=[
                Mod("1", "name1", {}),
                Mod("2", "name2", {Sites.modrinth: Site(Sites.modrinth)}),
            ],
            expected=[
                Mod("1", "name1", {}, upload_time=1337),
                Mod("2", "name2", {Sites.modrinth: Site(Sites.modrinth)}),
            ],
            db_after=[
                row("1", upload_time=1337),
                row("2", sites="modrinth::"),
            ],
        ),
    ],
)
def test_sync_with_dir(test: SyncWithDirTest, sqlite: Sqlite, db: sqlite3.Connection, cursor: sqlite3.Cursor):
    print(test.name)

    # Insert initial data
    for row in test.db_before:
        cursor.execute(
            "INSERT INTO mod (id, sites, upload_time, active) VALUES (?, ?, ?, ?)",
            row,
        )
    db.commit()

    # Sync with dir
    result = sqlite.sync_with_dir(test.input)

    assert result == test.expected

    # Test DB after sync
    cursor.execute("SELECT * FROM mod")
    rows = cursor.fetchall()

    assert rows == test.db_after


@pytest.mark.parametrize(
    "name,input,expected",
    [
        (
            "None when no input",
            "",
            None,
        ),
        (
            "None when only colons",
            "::",
            None,
        ),
        (
            "Set site name when specified",
            "curse::",
            {Sites.curse: Site(Sites.curse)},
        ),
        (
            "Slug but no id",
            "curse::slug",
            {Sites.curse: Site(Sites.curse, slug="slug")},
        ),
        (
            "All information",
            "curse:id:slug",
            {Sites.curse: Site(Sites.curse, "id", "slug")},
        ),
        (
            "Multiple sites",
            "curse:id:slug,modrinth::another-slug",
            {Sites.curse: Site(Sites.curse, "id", "slug"), Sites.modrinth: Site(Sites.modrinth, slug="another-slug")},
        ),
    ],
)
def test_string_sites_to_dict(name, input, expected):
    print(name)

    result = _Column.string_sites_to_dict(input)

    assert expected == result


@pytest.mark.parametrize(
    "name,input,expected",
    [
        (
            "Empty string when empty dict",
            {},
            "",
        ),
        (
            "Empty string when no dict",
            None,
            "",
        ),
        (
            "Set site name when specified",
            {Sites.curse: Site(Sites.curse)},
            "curse::",
        ),
        (
            "Slug but no id",
            {Sites.curse: Site(Sites.curse, slug="slug")},
            "curse::slug",
        ),
        (
            "All information",
            {Sites.curse: Site(Sites.curse, "id", "slug")},
            "curse:id:slug",
        ),
        (
            "Multiple sites",
            {Sites.curse: Site(Sites.curse, "id", "slug"), Sites.modrinth: Site(Sites.modrinth, slug="another-slug")},
            "curse:id:slug,modrinth::another-slug",
        ),
    ],
)
def test_dict_sites_to_string(name, input, expected):
    print(name)

    result = _Column.dict_sites_to_string(input)

    assert expected == result
