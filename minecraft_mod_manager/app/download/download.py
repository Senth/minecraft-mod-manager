from typing import List, Sequence

from tealprint import TealPrint

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...core.errors.download_failed import DownloadFailed
from ...core.errors.mod_file_invalid import ModFileInvalid
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...core.utils.latest_version_finder import LatestVersionFinder
from ...gateways.api.mod_finder import ModFinder
from ...gateways.http import MaxRetriesExceeded
from ...utils.log_colors import LogColors
from .download_repo import DownloadRepo


class Download:
    def __init__(self, repo: DownloadRepo, finder: ModFinder):
        self._repo = repo
        self._finder = finder

    def find_download_and_install(self, mods: Sequence[Mod]) -> None:
        mods_not_found: List[ModNotFoundException] = []
        corrupt_mods: List[Mod] = []

        download_queue: List[Mod] = []
        download_queue.extend(mods)

        # Find latest version of mod
        while len(download_queue) > 0:
            mod = download_queue.pop()
            try:
                TealPrint.info(mod.id, color=LogColors.header, push_indent=True)
                mod.sites = self._finder.find_mod(mod)

                versions = self._repo.get_versions(mod)
                latest_version = LatestVersionFinder.find_latest_version(mod, versions, filter=True)

                if latest_version:
                    # Different version
                    if latest_version.upload_time != mod.upload_time:
                        ok = self._download_latest_version(mod, latest_version)

                        # Add possible dependencies to download queue
                        if ok:
                            download_queue.extend(self._get_dependencies(latest_version))
                    else:
                        self.on_no_change(mod)
                else:
                    self.on_version_not_found(mod, versions)

            except ModNotFoundException as e:
                TealPrint.warning("🔺 Mod not found on any site...")
                mods_not_found.append(e)
            except MaxRetriesExceeded:
                TealPrint.warning("🔺 Max retries exceeded. Skipping...")
                mods_not_found.append(ModNotFoundException(mod))
            except ModFileInvalid:
                TealPrint.error("❌ Corrupted file.")
                corrupt_mods.append(mod)
            finally:
                TealPrint.pop_indent()

        self._print_errors(mods_not_found, corrupt_mods)

    def _download_latest_version(self, mod: Mod, latest_version: VersionInfo) -> bool:
        """Downloads and saves the latest version of the mod."""
        try:
            TealPrint.verbose("⬇ Downloading...")
            downloaded_mod = self._download(mod, latest_version)
            self._update_mod_from_file(downloaded_mod)
            self._repo.update_mod(downloaded_mod)
            self.on_new_version_downloaded(mod, downloaded_mod)
            return True
        except (DownloadFailed, MaxRetriesExceeded) as e:
            TealPrint.error(
                f"🔺 Download failed from {latest_version.site_name}",
            )
            TealPrint.error(str(e))
            return False
        except ModFileInvalid as e:
            # Remove temporary downloaded file
            self._repo.remove_mod_file(latest_version.filename)
            raise e

    def _get_dependencies(self, latest_version: VersionInfo) -> List[Mod]:
        if latest_version.dependencies:
            TealPrint.info("Add dependencies to download queue", push_indent=True)

        mods: List[Mod] = []

        for site, site_ids in latest_version.dependencies.items():
            for site_id in site_ids:
                mod = self._finder.get_mod_info(site, site_id)
                if mod:
                    TealPrint.info(f"➕ {mod.name}")
                    mods.append(mod)
                else:
                    TealPrint.warning(f"Dependency with id '{site_id}' not found on {site.value}")

        if latest_version.dependencies:
            TealPrint.pop_indent()
        return mods

    def _print_errors(self, mods_not_found, corrupt_mods) -> None:
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

    def on_new_version_downloaded(self, old: Mod, new: Mod) -> None:
        raise NotImplementedError("Not implemented in subclass")

    def on_no_change(self, mod: Mod) -> None:
        raise NotImplementedError("Not implemented in subclass")

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        raise NotImplementedError("Not implemented in subclass")

    def _update_mod_from_file(self, mod: Mod) -> None:
        if not config.pretend and mod.file:
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
            version=latest_version.number,
        )

        return add_mod
