from .downloader import Downloader
from .curse_api import CurseApi
from typing import List
from .config import config
from .db import Db
from . import web_driver
from .mod import Mod, RepoTypes
from .logger import Logger, LogColors
from .mod_not_found_exception import ModNotFoundException
from os import remove, path


class Updater:
    def __init__(self, db: Db) -> None:
        self._driver = web_driver.get()
        self._db = db
        self._curse_api = CurseApi(self._driver)
        self._downloader = Downloader()

    def update(self, installed_mods: List[Mod]) -> None:
        mods_to_update = Updater._filter_by_args(installed_mods)

        for mod in mods_to_update:
            latest_version = None
            was_unknown = mod.repo_type == RepoTypes.unknown

            # Curse
            try:
                if (
                    mod.repo_type == RepoTypes.curse
                    or mod.repo_type == RepoTypes.unknown
                ):
                    latest_version = self._curse_api.get_latest_version(mod)
            except ModNotFoundException as exception:
                Logger.error(str(exception), exit=True)

            # Update DB mod if a repo was found with a matching mod name
            if was_unknown and mod.repo_type != RepoTypes.unknown:
                self._db.update_mod(mod)

            if latest_version:
                # Only download if not same
                if mod.file != latest_version.filename:
                    downloaded_file = self._downloader.download(mod, latest_version)
                else:
                    downloaded_file = "skip"

                if downloaded_file:
                    # Remove old file
                    if downloaded_file != "skip":
                        Logger.info(
                            f"Updated {mod.repo_name_alias} ——> {latest_version.name}",
                            LogColors.green,
                        )
                        remove(path.join(config.dir, mod.file))
                        mod.file = downloaded_file

                    # Update DB
                    mod.upload_time = latest_version.upload_time
                    self._db.update_mod(mod)

    def close(self) -> None:
        if self._driver:
            self._driver.close()

    @staticmethod
    def _filter_by_args(installed_mods: List[Mod]) -> List[Mod]:
        if len(config.mods) == 0:
            return installed_mods

        mods_to_update: List[Mod] = []

        # Only add if supplied mods
        for repo_type, mod_id, repo_name_alias in config.mods:
            for mod in installed_mods:
                if (
                    mod.id == mod_id
                    or mod.id == repo_name_alias
                    or mod.repo_name_alias == mod_id
                    or mod.repo_name_alias == repo_name_alias
                ):
                    mods_to_update.append(mod)
                    break

        return mods_to_update