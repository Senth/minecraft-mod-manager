from typing import List, Sequence

from minecraft_mod_manager.gateways.http import MaxRetriesExceeded
from tealprint import TealPrint

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...core.errors.download_failed import DownloadFailed
from ...core.errors.mod_file_invalid import ModFileInvalid
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...core.utils.latest_version_finder import LatestVersionFinder
from ...utils.log_colors import LogColors
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
                TealPrint.info(mod.id, color=LogColors.header, push_indent=True)
                mod.sites = self._repo.search_for_mod(mod)

                versions = self._repo.get_versions(mod)
                latest_version = LatestVersionFinder.find_latest_version(mod, versions, filter=True)

                if latest_version:
                    TealPrint.verbose("⬇ Downloading...")
                    try:
                        downloaded_mod = self._download(mod, latest_version)
                        self._update_mod_from_file(downloaded_mod)
                        self._repo.update_mod(downloaded_mod)
                        self.on_version_found(mod, downloaded_mod)
                    except (DownloadFailed, MaxRetriesExceeded) as e:
                        TealPrint.error(
                            f"🔺 Download failed from {latest_version.site_name}",
                        )
                        TealPrint.error(str(e))
                    except ModFileInvalid:
                        # Remove temporary downloaded file
                        self._repo.remove_mod_file(latest_version.filename)
                        TealPrint.error("❌ Corrupted file.")
                        corrupt_mods.append(mod)
                else:
                    self.on_version_not_found(mod, versions)

            except ModNotFoundException as exception:
                TealPrint.warning("🔺 Mod not found on any site...")
                mods_not_found.append(exception)
            except MaxRetriesExceeded:
                TealPrint.warning("🔺 Max retries exceeded. Skipping...")
                mods_not_found.append(ModNotFoundException(mod))

            TealPrint.pop_indent()

        # Print errors
        if len(mods_not_found) > 0:
            TealPrint.warning(
                f"🔺 {len(mods_not_found)} mods not found",
                color=LogColors.header + LogColors.error,
                push_indent=True,
            )
            for error in mods_not_found:
                error.print_message()
            TealPrint.pop_indent()

        if len(corrupt_mods) > 0:
            TealPrint.warning(
                f"❌ {len(corrupt_mods)} corrupt mods",
                push_indent=True,
                color=LogColors.error + LogColors.header,
            )
            for mod in corrupt_mods:
                TealPrint.info(f"{mod.name}")
            TealPrint.pop_indent()

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
