import sqlite3
from os import path
from typing import Any, Dict, List, Union

from ..config import config
from ..core.entities.mod import Mod
from ..core.entities.sites import Site, Sites
from ..core.errors.mod_already_exists import ModAlreadyExists
from ..gateways.sqlite_upgrader import SqliteUpgrader
from ..utils.logger import LogColors, Logger


class _Column:
    c_id = "id"
    c_sites = "sites"
    c_upload_time = "upload_time"
    c_active = "active"

    def __init__(
        self,
        id: Any,
        sites: Any,
        upload_time: Any,
        active: Any,
    ) -> None:
        self.id = str(id)
        self.sites = _Column.string_sites_to_dict(sites)
        self.upload_time = int(upload_time)
        self.active = bool(active)

    @staticmethod
    def string_sites_to_dict(full_str: str) -> Union[Dict[Sites, Site], None]:
        if "," in full_str:
            sites_strings = full_str.split(",")
        else:
            sites_strings = [full_str]

        sites: Dict[Sites, Site] = {}
        for site_str in sites_strings:
            if len(site_str) == 0:
                continue

            name_str, id, slug = site_str.split(":")
            if len(name_str) == 0:
                continue

            if len(id) == 0:
                id = None
            if len(slug) == 0:
                slug = None

            try:
                name = Sites[name_str]
                sites[name] = Site(name, id, slug)
            except KeyError:
                Logger.error(f"DB site {site_str} not a valid site, full: '{full_str}'")

        if not sites:
            return None

        return sites

    @staticmethod
    def dict_sites_to_string(sites: Union[Dict[Sites, Site], None]) -> str:
        if not sites:
            return ""

        full_str = ""
        for site in sites.values():
            if len(full_str) > 0:
                full_str += ","

            id = ""
            if site.id:
                id = site.id

            slug = ""
            if site.slug:
                slug = site.slug

            full_str += f"{site.name.value}:{id}:{slug}"

        return full_str


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
                mod.upload_time = db_mod.upload_time

                # Update new mod sites info
                if isinstance(mod.sites, dict):
                    self.update_mod(mod)
                else:
                    mod.sites = db_mod.sites

        return mods

    def _get_mods(self) -> Dict[str, _Column]:
        self._cursor.execute(
            "SELECT "
            + f"{_Column.c_id}, "
            + f"{_Column.c_sites}, "
            + f"{_Column.c_upload_time}, "
            + f"{_Column.c_active} "
            + "FROM mod"
        )
        mods: Dict[str, _Column] = {}
        rows = self._cursor.fetchall()
        for row in rows:
            id, sites, upload_time, active = row
            mods[id] = _Column(
                id=id,
                sites=sites,
                upload_time=upload_time,
                active=active,
            )
        return mods

    def exists(self, id: str, filter_active: bool = True) -> bool:
        extra_filter = ""
        if filter_active:
            extra_filter = f"AND {_Column.c_active}=1"
        self._cursor.execute(f"SELECT 1 FROM mod WHERE {_Column.c_id}=? {extra_filter}", [id])
        return bool(self._cursor.fetchone())

    def update_mod(self, mod: Mod):
        if config.pretend:
            return

        if self.exists(mod.id, filter_active=False):
            self._cursor.execute(
                "UPDATE mod SET "
                + f"{_Column.c_sites}=?, "
                + f"{_Column.c_upload_time}=? "
                + "WHERE "
                + f"{_Column.c_id}=?",
                [_Column.dict_sites_to_string(mod.sites), mod.upload_time, mod.id],
            )
            self._connection.commit()
        else:
            self.insert_mod(mod)

    def insert_mod(self, mod: Mod):
        if config.pretend:
            return

        try:
            self._cursor.execute(
                "INSERT INTO mod ("
                + f"{_Column.c_id}, "
                + f"{_Column.c_sites}, "
                + f"{_Column.c_upload_time}, "
                + f"{_Column.c_active}) "
                + "VALUES (?, ?, ?, 1)",
                [mod.id, _Column.dict_sites_to_string(mod.sites), mod.upload_time],
            )
            self._connection.commit()
        except sqlite3.IntegrityError:
            raise ModAlreadyExists(mod)

    def _activate_mod(self, id: str):
        if config.pretend:
            return

        Logger.debug(f"Reactivate mod {id} in DB", LogColors.add)
        self._cursor.execute(f"UPDATE mod SET {_Column.c_active}=1 WHERE {_Column.c_id}=?", [id])
        self._connection.commit()

    def _inactivate_mod(self, id: str):
        if config.pretend:
            return

        Logger.debug(f"Inactivate mod {id} in DB", LogColors.remove)
        self._cursor.execute(f"UPDATE mod SET {_Column.c_active}=0 WHERE {_Column.c_id}=?", [id])
        self._connection.commit()
