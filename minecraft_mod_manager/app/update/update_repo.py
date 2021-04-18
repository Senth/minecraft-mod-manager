from typing import Sequence

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo
from ..download.download_repo import DownloadRepo


class UpdateRepo(DownloadRepo):
    def get_latest_version(self, mod: ModArg) -> VersionInfo:
        raise NotImplementedError()

    def get_all_mods(self) -> Sequence[Mod]:
        raise NotImplementedError()
