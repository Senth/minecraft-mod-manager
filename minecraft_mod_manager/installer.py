from typing import List, Union
from . import web_driver
from .logger import Logger, LogColors
from .mod_not_found_exception import ModNotFoundException
from .mod import ModArg, Mod, RepoTypes
from .downloader import Downloader
from .curse_api import CurseApi
from .db import Db
from .version_info import VersionInfo
from pathlib import Path


class Installer:
    def __init__(self, db: Db, installed_mods: List[Mod]) -> None:
        self._driver = web_driver.get()
        self._db = db
        self._curse_api = CurseApi(self._driver)
        self._installed_mods = installed_mods

    def install(self, mods: List[ModArg]) -> None:
        max_width = 0
        for mod in mods:
            if len(mod.id) > max_width:
                max_width = len(mod.id)

        for mod in mods:
            if self._is_already_installed(mod):
                Logger.info(
                    f"{mod.id} has already been installed, skipping...", LogColors.skip
                )

            latest_version: Union[VersionInfo, None] = None
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

            if latest_version:
                downloaded_mod = self._download(mod, latest_version, max_width)

                if downloaded_mod:
                    self._db.insert_mod(downloaded_mod)

    def _download(
        self, mod: ModArg, latest_version: VersionInfo, max_width: int
    ) -> Union[Mod, None]:
        downloaded_file = Downloader().download(latest_version)

        if downloaded_file:
            name = f"{mod.id}".ljust(max_width)
            Logger.info(
                f"Installed {name} ——> {latest_version.name}",
                LogColors.green,
            )

            add_mod = Mod(
                id=mod.id,
                name=mod.id,
                name_in_repo=mod.name_in_repo,
                repo_type=mod.repo_type,
                file=downloaded_file,
                upload_time=latest_version.upload_time,
            )

            return add_mod

    def _is_already_installed(self, mod: ModArg) -> bool:
        for installed_mod in self._installed_mods:
            if installed_mod.id == mod.id or installed_mod.name == mod.id:
                return True

        return False

    def close(self) -> None:
        if self._driver:
            self._driver.close()
