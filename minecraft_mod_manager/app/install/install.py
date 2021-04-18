from typing import List, Sequence

from ...core.entities.mod import Mod, ModArg
from ...utils.logger import LogColors, Logger
from ..download.download import Download
from .install_repo import InstallRepo


class Install(Download):
    def __init__(self, repo: InstallRepo) -> None:
        super().__init__(repo, "Installed")
        self._repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods = self._filter_installed_mods(mods)
        self.find_download_and_install(mods)

    def _filter_installed_mods(self, mods: Sequence[ModArg]) -> Sequence[Mod]:
        mods_to_install: List[Mod] = []

        for mod in mods:
            if not self._repo.is_installed(mod.id):
                mods_to_install.append(Mod.fromModArg(mod))
            else:
                Logger.info(f"{mod.id} has already been installed, skipping...", LogColors.skip)

        return mods_to_install
