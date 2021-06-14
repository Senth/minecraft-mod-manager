import sqlite3

from ..core.entities.sites import Sites


class SqliteUpgrader:
    _version = 2

    def __init__(self, connection: sqlite3.Connection, cursor: sqlite3.Cursor) -> None:
        self._connection = connection
        self._cursor = cursor

    def upgrade(self):
        # First run time
        if not self._mod_table_exists():
            self._create_version_table()
            self._create_mod_table()
            self._connection.commit()
            return

        version = self._get_version()

        # Upgrade tables one version at a time
        if version <= 0:
            self._v0_to_v1()
        if version <= 1:
            self._v1_to_v2()

        # Update version
        self._cursor.execute("UPDATE version SET version=?", [SqliteUpgrader._version])
        self._connection.commit()

    def _get_version(self) -> int:
        if self._version_table_exists():
            self._cursor.execute("SELECT version FROM version")
            return int(self._cursor.fetchone()[0])
        return 0

    def _version_table_exists(self):
        self._cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='version'")
        return self._cursor.fetchone()[0] == 1

    def _mod_table_exists(self):
        self._cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='mod'")
        return self._cursor.fetchone()[0] == 1

    def _create_mod_table(self):
        self._create_mod_table_v2()

    def _create_mod_table_v1(self):
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS mod ("
            + "id TEXT UNIQUE, "
            + "site TEXT, "
            + "site_id TEXT, "
            + "site_slug TEXT, "
            + "upload_time INTEGER, "
            + "active INTEGER)"
        )

    def _create_mod_table_v2(self):
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS mod ("
            + "id TEXT UNIQUE, "
            + "sites TEXT, "
            + "upload_time INTEGER, "
            + "active INTEGER)"
        )

    def _create_version_table(self):
        self._cursor.execute("CREATE TABLE IF NOT EXISTS version (version INTEGER)")
        self._cursor.execute("INSERT INTO version (version) VALUES (?)", [SqliteUpgrader._version])

    def _v0_to_v1(self):
        # Just remove mod table and create it again...
        self._cursor.execute("DROP TABLE mod")
        self._create_mod_table_v1()
        self._create_version_table()
        self._connection.commit()

    def _v1_to_v2(self):
        self._cursor.execute("SELECT * FROM mod")
        rows = self._cursor.fetchall()
        self._cursor.execute("DROP TABLE mod")
        self._create_mod_table_v2()

        for row in rows:
            id, site, site_id, site_slug, upload_time, active = row

            combined_site = ""
            if site:
                try:
                    if site_id == "None":
                        site_id = ""
                    if site_slug == "None":
                        site_slug = ""

                    valid_site = Sites[site]
                    combined_site = f"{valid_site.value}:{site_id}:{site_slug}"
                except KeyError:
                    # Skip if the site is invalid 'unknown'
                    pass

            new = (id, combined_site, upload_time, active)
            self._cursor.execute("INSERT INTO mod (id, sites, upload_time, active) VALUES (?, ?, ?, ?)", new)

        self._connection.commit()
