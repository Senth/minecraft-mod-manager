import sqlite3


class _Column:
    c_id = "id"
    c_repo_id = "repo_id"
    c_repo_type = "repo_type"
    c_repo_alias = "repo_alias"
    c_upload_time = "upload_time"
    c_active = "active"

    def __init__(
        self,
        id: str,
        repo_id: str,
        repo_type: str,
        repo_alias: str,
        upload_time: int,
        active: bool,
    ) -> None:
        self.id = id
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.repo_alias = repo_alias
        self.upload_time = upload_time
        self.active = active


class SqliteUpgrader:
    _version = 1

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
        self._connection.execute(
            "CREATE TABLE IF NOT EXISTS mod ("
            + f"{_Column.c_id} TEXT UNIQUE, "
            + f"{_Column.c_repo_id} TEXT, "
            + f"{_Column.c_repo_type} TEXT, "
            + f"{_Column.c_repo_alias} TEXT, "
            + f"{_Column.c_upload_time} INTEGER, "
            + f"{_Column.c_active} INTEGER)"
        )

    def _create_version_table(self):
        self._connection.execute("CREATE TABLE IF NOT EXISTS version (version INTEGER)")
        self._connection.execute("INSERT INTO version (version) VALUES (?)", [SqliteUpgrader._version])

    def _v0_to_v1(self):
        # Just remove mod table and create it again...
        self._connection.execute("DROP TABLE mod")
        self._create_mod_table()
        self._create_version_table()
        self._connection.commit()
