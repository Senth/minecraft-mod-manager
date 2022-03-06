from typing import List, Sequence

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...core.errors.download_failed import DownloadFailed
from ...core.errors.mod_file_invalid import ModFileInvalid
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...core.utils.latest_version_finder import LatestVersionFinder
from ...utils.logger import LogColors, Logger
from .download_repo import DownloadRepo


class Download:
    def __init__(self, repo: DownloadRepo):
        self._repo = repo

    def find_download_and_install(self, mods: Sequence[Mod]) -> None:
        mods_not_found: List[ModNotFoundException] = []
        corrupt_mods: List[Mod] = []

        # Find latest version of mod
        for mod in mods:
            try:
                Logger.info(mod.id, LogColors.bold)
                mod.sites = self._repo.search_for_mod(mod)

                versions = self._repo.get_versions(mod)
                latest_version = LatestVersionFinder.find_latest_version(mod, versions, filter=True)

                if latest_version:
                    Logger.verbose("⬇ Downloading...", indent=1)
                    try:
                        downloaded_mod = self._download(mod, latest_version)
                        self._update_mod_from_file(downloaded_mod)
                        self._repo.update_mod(downloaded_mod)
                        self.on_version_found(mod, downloaded_mod)
                    except DownloadFailed as e:
                        Logger.info(
                            f"🔺 Download failed from {latest_version.site_name}. Might be user-agent error.",
                            LogColors.red,
                            indent=1,
                        )
                        Logger.error(str(e), indent=1)
                        pass
                    except ModFileInvalid:
                        # Remove temporary downloaded file
                        self._repo.remove_mod_file(latest_version.filename)
                        Logger.info("❌ Corrupted file.", LogColors.red, indent=1)
                        corrupt_mods.append(mod)
                        continue

                else:
                    self.on_version_not_found(mod, versions)

            except ModNotFoundException as exception:
                Logger.info("🔺 Mod not found on any site...", LogColors.red, indent=1)
                mods_not_found.append(exception)

        # Print errors
        if len(mods_not_found) > 0:
            Logger.info("🔺 Mods not found", LogColors.bold + LogColors.red)
            for error in mods_not_found:
                error.print_message()

        if len(corrupt_mods) > 0:
            Logger.info("❌ Corrupted mods.")
            for mod in corrupt_mods:
                Logger.info(f"{mod.name}", indent=1)

    def on_version_found(self, old: Mod, new: Mod) -> None:
        raise NotImplementedError("Not implemented in subclass")

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        raise NotImplementedError("Not implemented in subclass")

    def _update_mod_from_file(self, mod: Mod) -> None:
        if mod.file:
            installed_mod = self._repo.get_mod_from_file(mod.file)
            if installed_mod:
                mod.id = installed_mod.id
                mod.name = installed_mod.name
                mod.version = installed_mod.version

    def _download(self, mod: ModArg, latest_version: VersionInfo) -> Mod:
        downloaded_file = self._repo.download(latest_version.download_url, latest_version.filename)
        sites = mod.sites
        if not sites:
            sites = {}

        add_mod = Mod(
            id=mod.id,
            name=mod.id,
            sites=sites,
            file=downloaded_file.name,
            upload_time=latest_version.upload_time,
        )

        return add_mod
