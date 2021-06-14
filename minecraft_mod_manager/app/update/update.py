from typing import List, Sequence

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ...utils.logger import LogColors, Logger
from ..download.download import Download, DownloadInfo
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

    def on_version_found(self, download_info: DownloadInfo) -> None:
        if download_info.mod.file and not config.pretend:
            self._update_repo.remove_mod_file(download_info.mod.file)
        # TODO #32 improve message
        Logger.info(
            f"🟢 Updated -> {download_info.version_info.filename}",
            LogColors.green,
            indent=1,
        )

    def on_version_not_found(self, mod: Mod, versions: List[VersionInfo]) -> None:
        Logger.verbose("🟨 No new version found", LogColors.skip, indent=1)
