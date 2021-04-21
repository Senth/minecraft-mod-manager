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

    def find_download_and_install(self, mods: Sequence[Mod]) -> None:
        mods_not_found: List[ModNotFoundException] = []

        # Find latest version of mod
        for mod in mods:
            try:
                Logger.info(mod.id, LogColors.bold)
                latest_version = self._repo.get_latest_version(mod)

                if latest_version:
                    download_info = DownloadInfo(mod, latest_version)
                    Logger.verbose("⬇ Downloading...", indent=1)
                    self._download_and_install(download_info)
                    Logger.info(
                        f"🟢 {self._success_prefix} -> {download_info.version_info.filename}",
                        LogColors.green,
                        indent=1,
                    )
                else:
                    Logger.verbose("🟨 No new version found", LogColors.skip, indent=1)

            except ModNotFoundException as exception:
                Logger.error("🔺 Mod not found on any site...", indent=1)
                mods_not_found.append(exception)

        # Print errors
        if len(mods_not_found) > 0:
            errorMessage = ""
            for error in mods_not_found:
                errorMessage += str(error) + "\n\n"
            Logger.error(errorMessage)

    def _download_and_install(self, download_info: DownloadInfo) -> None:
        downloaded_mod = self._download(download_info.mod, download_info.version_info)
        self._repo.update_mod(downloaded_mod)

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
