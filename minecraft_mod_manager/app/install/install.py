from datetime import datetime
from typing import Dict, List, Sequence

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.version_info import VersionInfo
from ...core.utils.latest_version_finder import LatestVersionFinder
from ...utils.logger import LogColors, Logger
from ..download.download import Download, DownloadInfo
from .install_repo import InstallRepo


class Install(Download):
    def __init__(self, repo: InstallRepo) -> None:
        super().__init__(repo)
        self._install_repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods = self._filter_installed_mods(mods)
        mods = self._set_mod_loader(mods)
        self.find_download_and_install(mods)

    def _filter_installed_mods(self, mods: Sequence[ModArg]) -> Sequence[Mod]:
        mods_to_install: List[Mod] = []

        for mod in mods:
            if not self._install_repo.is_installed(mod.id):
                mods_to_install.append(Mod.fromModArg(mod))
            else:
                Logger.info(f"{mod.id} has already been installed, skipping...", LogColors.skip)

        return mods_to_install

    def _set_mod_loader(self, mods: Sequence[Mod]) -> Sequence[Mod]:
        loader = self._get_mod_loader_to_use()
        if loader != ModLoaders.unknown:
            for mod in mods:
                mod.mod_loader = loader
        return mods

    def _get_mod_loader_to_use(self) -> ModLoaders:
        mods = self._install_repo.get_all_mods()

        # Count
        counts: Dict[ModLoaders, int] = {}
        for mod in mods:
            loader = mod.mod_loader
            if loader != ModLoaders.unknown:
                count = 0
                if loader in counts:
                    count = counts[loader]
                counts[loader] = count + 1

        # Sort
        count_max = 0
        loader_max = ModLoaders.unknown

        for loader, count in counts.items():
            if count > count_max:
                count_max = count
                loader_max = loader
            # Multiple max, use none then
            elif count == count_max:
                loader_max = ModLoaders.unknown

        return loader_max

    def on_version_found(self, download_info: DownloadInfo) -> None:
        # TODO #32 improve message
        Logger.info(
            f"🟢 Installed ({download_info.version_info.filename})",
            LogColors.green,
            indent=1,
        )

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        Logger.info(f"🟨 All versions were filtered out", LogColors.skip, indent=1)

        latest_unfiltered = LatestVersionFinder.find_latest_version(mod, versions, filter=False)
        if latest_unfiltered:
            Install._print_latest_unfiltered(mod, latest_unfiltered)

    @staticmethod
    def _print_latest_unfiltered(mod: Mod, latest: VersionInfo) -> None:
        if config.filter.version and config.filter.version not in latest.minecraft_versions:
            Logger.info("The latest version was filtered out by minecraft version", indent=2)
            Logger.info(f"Run without {LogColors.command}--minecraft-version{LogColors.no_color}, or")
            Logger.info(
                f"run with {LogColors.command}--minecraft-version VERSION{LogColors.no_color} to download it", indent=3
            )
            Logger.info(str(latest.minecraft_versions), indent=3)

        if LatestVersionFinder.is_filtered_by_stability(latest):
            Logger.info("The latest version was filtered out by stability", indent=2)
            Logger.info(
                f"Run with {LogColors.command}--{latest.stability.value}{LogColors.no_color} to download it", indent=3
            )

        if LatestVersionFinder.is_filtered_by_mod_loader(mod.mod_loader, latest):
            Logger.info("The latest versios was filtered out by mod loader", indent=2)
            Logger.info(
                f"Run with {LogColors.command}--mod_loader {next(iter(latest.mod_loaders))}{LogColors.command} to download it",
                indent=3,
            )

        Logger.verbose("Latest version", LogColors.bold, indent=2)
        width = 20
        Logger.verbose("Upload date:".ljust(width) + str(datetime.fromtimestamp(latest.upload_time)), indent=3)
        Logger.verbose("Stability:".ljust(width) + latest.stability.value, indent=3)
        Logger.verbose("Minecraft versions:".ljust(width) + str(latest.minecraft_versions), indent=3)
        Logger.verbose("Filename:".ljust(width) + latest.filename, indent=3)
