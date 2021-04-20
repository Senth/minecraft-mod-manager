from typing import Dict, List, Sequence

from ...core.entities.mod import Mod, ModArg
from ...core.entities.mod_loaders import ModLoaders
from ...utils.logger import LogColors, Logger
from ..download.download import Download
from .install_repo import InstallRepo


class Install(Download):
    def __init__(self, repo: InstallRepo) -> None:
        super().__init__(repo, "Installed")
        self._repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods = self._filter_installed_mods(mods)
        mods = self._set_mod_loader(mods)
        self.find_download_and_install(mods)

    def _filter_installed_mods(self, mods: Sequence[ModArg]) -> Sequence[Mod]:
        mods_to_install: List[Mod] = []

        for mod in mods:
            if not self._repo.is_installed(mod.id):
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
        mods = self._repo.get_all_mods()

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
