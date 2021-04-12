from typing import List, Tuple

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...utils.logger import LogColors, Logger
from .install_repo import InstallRepo


class Install:
    def __init__(self, repo: InstallRepo) -> None:
        self._repo = repo

    def execute(self, mods: List[ModArg]) -> None:
        mods_to_install: List[Tuple[ModArg, VersionInfo]] = []
        mods_not_found: List[ModNotFoundException] = []
        max_name_width = 0

        # Find latest version of mod
        for mod in mods:
            if self._repo.is_installed(mod):
                Logger.info(f"{mod.id} has already been installed, skipping...", LogColors.skip)
                continue

            try:
                latest_version = self._repo.get_latest_version(mod)
                mods_to_install.append((mod, latest_version))

                if len(mod.id) > max_name_width:
                    max_name_width = len(mod.id)
            except ModNotFoundException as exception:
                mods_not_found.append(exception)

        # Print errors
        if len(mods_not_found) > 0:
            errorMessage = ""
            for error in mods_not_found:
                errorMessage += str(error) + "\n\n"

            Logger.error(errorMessage, exit=True)

        # Download
        for (mod, latest_version) in mods_to_install:
            downloaded_mod = self._download(mod, latest_version)
            self._repo.insert_mod(downloaded_mod)

            name = f"{mod.id}".ljust(max_name_width)
            Logger.info(
                f"Installed {name} ——> {latest_version.name}",
                LogColors.green,
            )

    def _download(self, mod: ModArg, latest_version: VersionInfo) -> Mod:
        downloaded_file = self._repo.download(latest_version.download_url, latest_version.filename)

        add_mod = Mod(
            id=mod.id,
            name=mod.id,
            alias=mod.alias,
            repo_type=mod.repo_type,
            file=downloaded_file.name,
            upload_time=latest_version.upload_time,
        )

        return add_mod
