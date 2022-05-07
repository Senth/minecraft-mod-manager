from datetime import datetime
from typing import Dict, List, Sequence

from tealprint import TealPrint

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.version_info import VersionInfo
from ...core.utils.latest_version_finder import LatestVersionFinder
from ...gateways.api.mod_finder import ModFinder
from ...utils.log_colors import LogColors
from ..download.download import Download
from .install_repo import InstallRepo


class Install(Download):
    def __init__(self, repo: InstallRepo, finder: ModFinder) -> None:
        super().__init__(repo, finder)
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
                TealPrint.info(mod.id, color=LogColors.header, push_indent=True)
                TealPrint.info("Skipping... has already been installed", color=LogColors.skip, pop_indent=True)

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

    def on_new_version_downloaded(self, old: Mod, new: Mod) -> None:
        TealPrint.info(
            f"🟢 Installed version {new.version}",
            color=LogColors.add,
        )

    def on_no_change(self, mod: Mod) -> None:
        TealPrint.verbose("🔵 Already installed and up-to-date")

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        TealPrint.info("🟨 All versions were filtered out", color=LogColors.skip, push_indent=True)

        latest_unfiltered = LatestVersionFinder.find_latest_version(mod, versions, filter=False)
        if latest_unfiltered:
            Install._print_latest_unfiltered(mod, latest_unfiltered)
        TealPrint.pop_indent()

    @staticmethod
    def _print_latest_unfiltered(mod: Mod, latest: VersionInfo) -> None:
        if config.filter.version and config.filter.version not in latest.minecraft_versions:
            TealPrint.info("The latest version was filtered out by minecraft version")
            TealPrint.info(
                f"Run without {LogColors.command}--minecraft-version{LogColors.no_color}, or",
                push_indent=True,
            )
            TealPrint.info(
                f"run with {LogColors.command}--minecraft-version VERSION{LogColors.no_color} to download it",
                pop_indent=True,
            )

        if LatestVersionFinder.is_filtered_by_stability(latest):
            TealPrint.info("The latest version was filtered out by stability", push_indent=True)
            TealPrint.info(
                f"Run with {LogColors.command}--{latest.stability.value}{LogColors.no_color} to download it",
                pop_indent=True,
            )

        if LatestVersionFinder.is_filtered_by_mod_loader(mod.mod_loader, latest):
            TealPrint.info("The latest versios was filtered out by mod loader", push_indent=True)
            TealPrint.info(
                f"Run with {LogColors.command}--mod_loader {next(iter(latest.mod_loaders))}{LogColors.no_color} "
                + "to download it",
                pop_indent=True,
            )

        TealPrint.info("Latest version", color=LogColors.header, push_indent=True)
        width = 20
        TealPrint.info("Upload date:".ljust(width) + str(datetime.fromtimestamp(latest.upload_time)))
        TealPrint.info("Stability:".ljust(width) + latest.stability.value)
        TealPrint.info("Minecraft versions:".ljust(width) + str(latest.minecraft_versions))
        TealPrint.verbose("Filename:".ljust(width) + latest.filename, pop_indent=True)
