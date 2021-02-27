from .downloader import Downloader
from .curse_api import CurseApi
from typing import List
from .config import config
from .db import Db
from . import web_driver
from .mod import Mod, RepoTypes
from .logger import Logger, LogColors
from .mod_not_found_exception import ModNotFoundException
from .version_info import VersionInfo
from os import remove, path


class Updater:
    def __init__(self, db: Db) -> None:
        self._driver = web_driver.get()
        self._db = db
        self._curse_api = CurseApi(self._driver)

    def update(self, installed_mods: List[Mod]) -> None:
        mods_to_update = Updater._filter_by_args(installed_mods)

        max_width = 0
        for mod in mods_to_update:
            name = f"{mod.name_in_repo} {mod.version}"
            if len(name) > max_width:
                max_width = len(name)

        for mod in mods_to_update:
            latest_version = None
            was_unknown = mod.repo_type == RepoTypes.unknown

            # Curse
            try:
                if (
                    mod.repo_type == RepoTypes.curse
                    or mod.repo_type == RepoTypes.unknown
                ):
                    mod.repo_type = RepoTypes.curse
                    latest_version = self._curse_api.get_latest_version(mod)
            except ModNotFoundException as exception:
                Logger.error(str(exception), exit=True)

            # Update DB mod if a repo was found with a matching mod name
            if was_unknown and mod.repo_type != RepoTypes.unknown:
                self._db.update_mod(mod)

            updated = False

            if latest_version:
                updated = self._download(mod, latest_version, max_width)

            if not updated:
                self._write_no_update(mod)

    def _download(self, mod: Mod, latest_version: VersionInfo, max_width: int) -> bool:
        """Return true if the mod has been downloaded and updated"""
        updated = False

        # Only update if filename isn't the same
        if mod.file != latest_version.filename:
            downloaded_file = Downloader.download(latest_version)
        else:
            downloaded_file = "skip"

        if downloaded_file:
            # Remove old file
            if downloaded_file != "skip":
                updated = True
                current = f"{mod.name_in_repo} {mod.version}".ljust(max_width)
                Logger.info(
                    f"{current} ——> {latest_version.name}",
                    LogColors.green,
                )
                if not config.pretend:
                    remove(path.join(config.dir, mod.file))
                mod.file = downloaded_file

            # Update DB
            mod.upload_time = latest_version.upload_time
            self._db.update_mod(mod)

        return updated

    def _write_no_update(self, mod: Mod) -> None:
        Logger.info(f"No update for {mod.name_in_repo}", LogColors.yellow)

    def close(self) -> None:
        if self._driver:
            self._driver.close()

    @staticmethod
    def _filter_by_args(installed_mods: List[Mod]) -> List[Mod]:
        if len(config.mods) == 0:
            return installed_mods

        mods_to_update: List[Mod] = []

        # Only add if supplied mods
        for mod_arg in config.mods:
            for mod in installed_mods:
                if (
                    mod.id == mod_arg.id
                    or mod.id == mod_arg.name_in_repo
                    or mod.name_in_repo == mod_arg.id
                    or mod.name_in_repo == mod_arg.name_in_repo
                ):
                    mods_to_update.append(mod)
                    break

        return mods_to_update
