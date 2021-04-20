from typing import List, Sequence

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...utils.logger import LogColors, Logger
from .download_repo import DownloadRepo


class DownloadInfo:
    def __init__(self, mod: Mod, version_info: VersionInfo):
        self.mod = mod
        self.version_info = version_info

    @property
    def name(self) -> str:
        name = f"{self.mod.id}"

        if self.mod.version:
            name += f" {self.mod.version}"

        return name


class Download:
    def __init__(self, repo: DownloadRepo, success_prefix: str):
        self._repo = repo
        self._success_prefix = success_prefix
        self._name_width_max = 0

    def find_download_and_install(self, mods: Sequence[Mod]) -> None:
        mods_to_install = self._find_latest_versions(mods)
        self._download_and_install(mods_to_install)

    def _find_latest_versions(self, mods: Sequence[Mod]) -> Sequence[DownloadInfo]:
        mods_to_install: List[DownloadInfo] = []
        mods_not_found: List[ModNotFoundException] = []

        # Find latest version of mod
        for mod in mods:
            try:
                latest_version = self._repo.get_latest_version(mod)
                download_info = DownloadInfo(mod, latest_version)
                mods_to_install.append(download_info)

            except ModNotFoundException as exception:
                mods_not_found.append(exception)

        # Print errors
        if len(mods_not_found) > 0:
            errorMessage = ""
            for error in mods_not_found:
                errorMessage += str(error) + "\n\n"
            Logger.error(errorMessage, exit=True)

        return mods_to_install

    def _download_and_install(self, downloads: Sequence[DownloadInfo]):
        # Check max name width
        for download_info in downloads:
            name_width = len(download_info.name)
            if name_width > self._name_width_max:
                self._name_width_max = name_width

        # Download
        for download_info in downloads:
            downloaded_mod = self._download(download_info.mod, download_info.version_info)
            self._repo.update_mod(downloaded_mod)
            self._print_installed(download_info)

    def _print_installed(self, download_info: DownloadInfo) -> None:
        name = download_info.name.ljust(self._name_width_max)
        Logger.info(
            f"{self._success_prefix} {name} -> {download_info.version_info.name}",
            LogColors.green,
        )

    def _download(self, mod: ModArg, latest_version: VersionInfo) -> Mod:
        downloaded_file = self._repo.download(latest_version.download_url, latest_version.filename)

        add_mod = Mod(
            id=mod.id,
            name=mod.id,
            site_slug=mod.site_slug,
            site=mod.site,
            file=downloaded_file.name,
            upload_time=latest_version.upload_time,
        )

        return add_mod
