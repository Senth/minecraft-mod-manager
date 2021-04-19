import sqlite3
from os import path
from typing import Dict, List

from minecraft_mod_manager.gateways.sqlite_upgrader import SqliteUpgrader

from ..config import config
from ..core.entities.mod import Mod
from ..core.entities.repo_types import RepoTypes
from ..core.errors.mod_already_exists import ModAlreadyExists
from ..utils.logger import LogColors, Logger
from .sqlite_upgrader import _Column


class Sqlite:
    def __init__(self) -> None:
        file_path = path.join(config.dir, f".{config.app_name}.db")
        Logger.debug(f"DB location: {file_path}")
        self._connection = sqlite3.connect(file_path)
        self._cursor = self._connection.cursor()

        upgrader = SqliteUpgrader(self._connection, self._cursor)
        upgrader.upgrade()

    def close(self) -> None:
        self._cursor.close()
        self._connection.commit()
        self._connection.close()

    def sync_with_dir(self, mods: List[Mod]) -> List[Mod]:
        """Synchronize DB with the mods in the folder. This makes sure that we don't download
        mods that have been removed manually.

        Args:
            mods (List[Mod]): Mods present in the mods directory

        Returns:
            List[Mod]: Updated list with mod info
        """
        mods = mods.copy()
        mods_to_add = mods.copy()

        # Go through all existing mods in the DB and see which should be added and removed
        db_mods = self._get_mods()
        for db_mod in db_mods.values():
            # Search for existing info
            found = False
            for mod in mods_to_add:
                if mod.id == db_mod.id:
                    found = True
                    mods_to_add.remove(mod)
                    Logger.debug(f"Found mod {mod.id} in DB", LogColors.found)

                    # Reactivate mod
                    if not db_mod.active:
                        self._activate_mod(mod.id)
                    break

            # Inactivate mod
            if not found:
                self._inactivate_mod(db_mod.id)

        # Add mods
        for mod in mods_to_add:
            Logger.debug(f"Adding mod {mod.id} to DB", LogColors.add)
            self.insert_mod(mod)

        # Update mod info
        for mod in mods:
            if mod.id in db_mods:
                db_mod = db_mods[mod.id]
                mod.repo_type = RepoTypes[db_mod.repo_type]
                mod.repo_alias = db_mod.repo_alias
                mod.upload_time = db_mod.upload_time

        return mods

    def _get_mods(self) -> Dict[str, _Column]:
        self._cursor.execute(
            "SELECT "
            + f"{_Column.c_id}, "
            + f"{_Column.c_repo_id}, "
            + f"{_Column.c_repo_type}, "
            + f"{_Column.c_repo_alias}, "
            + f"{_Column.c_upload_time}, "
            + f"{_Column.c_active} "
            + "FROM mod"
        )
        mods: Dict[str, _Column] = {}
        rows = self._cursor.fetchall()
        for row in rows:
            id = str(row[0])
            repo_id = row[1]
            repo_type = row[2]
            repo_name = row[3]
            upload_time = int(row[4])
            active = bool(row[5])
            mods[id] = _Column(
                id=id,
                repo_id=repo_id,
                repo_type=repo_type,
                repo_alias=repo_name,
                upload_time=upload_time,
                active=active,
            )
        return mods

    def exists(self, id: str) -> bool:
        self._cursor.execute(f"SELECT 1 FROM mod WHERE {_Column.c_id}=?", [id])
        return bool(self._cursor.fetchone())

    def update_mod(self, mod: Mod):
        if config.pretend:
            return

        if self.exists(mod.id):
            self._connection.execute(
                "UPDATE mod SET "
                + f"{_Column.c_repo_id}=?, "
                + f"{_Column.c_repo_type}=?, "
                + f"{_Column.c_repo_alias}=?, "
                + f"{_Column.c_upload_time}=? "
                + "WHERE "
                + f"{_Column.c_id}=?",
                [mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time, mod.id],
            )
            self._connection.commit()
        else:
            self.insert_mod(mod)

    def insert_mod(self, mod: Mod):
        if config.pretend:
            return

        try:
            self._connection.execute(
                "INSERT INTO mod ("
                + f"{_Column.c_id}, "
                + f"{_Column.c_repo_id}, "
                + f"{_Column.c_repo_type}, "
                + f"{_Column.c_repo_alias}, "
                + f"{_Column.c_upload_time}, "
                + f"{_Column.c_active}) "
                + "VALUES (?, ?, ?, ?, ?, 1)",
                [mod.id, mod.repo_id, mod.repo_type.value, mod.repo_alias, mod.upload_time],
            )
            self._connection.commit()
        except sqlite3.IntegrityError:
            raise ModAlreadyExists(mod)

    def _activate_mod(self, id: str):
        if config.pretend:
            return

        Logger.debug(f"Reactivate mod {id} in DB", LogColors.add)
        self._connection.execute(f"UPDATE mod SET {_Column.c_active}=1 WHERE {_Column.c_id}=?", [id])
        self._connection.commit()

    def _inactivate_mod(self, id: str):
        if config.pretend:
            return

        Logger.debug(f"Inactivate mod {id} in DB", LogColors.remove)
        self._connection.execute(f"UPDATE mod SET {_Column.c_active}=0 WHERE {_Column.c_id}=?", [id])
        self._connection.commit()