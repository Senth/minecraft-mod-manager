from typing import List, Sequence

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...utils.logger import LogColors, Logger
from ..download.download import Download
from .update_repo import UpdateRepo


class Update(Download):
    def __init__(self, repo: UpdateRepo) -> None:
        super().__init__(repo)
        self._update_repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods_to_update: List[Mod] = []

        # Use all installed mods if mods is empty
        if len(mods) == 0:
            mods_to_update = list(self._update_repo.get_all_mods())
        else:
            for mod_arg in mods:
                mod = self._update_repo.get_mod(mod_arg.id)
                if mod:
                    mods_to_update.append(mod)

        self.find_download_and_install(mods_to_update)

    def on_version_found(self, old: Mod, new: Mod) -> None:
        if new.file:
            if Update._has_downloaded_new_file(old, new):
                if not config.pretend and old.file:
                    self._update_repo.remove_mod_file(old.file)

                Logger.info(
                    f"🟢 Updated {old.version} -> {new.version}",
                    LogColors.green,
                    indent=1,
                )

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        Logger.verbose("🟨 No new version found", LogColors.skip, indent=1)

    @staticmethod
    def _has_downloaded_new_file(old: Mod, new: Mod) -> bool:
        if new.file and len(new.file) > 0:
            if old.file != new.file:
                return True

        return False
