from typing import Sequence

from ...core.entities.mod import Mod
from ..download.download_repo import DownloadRepo


class InstallRepo(DownloadRepo):
    def is_installed(self, id: str) -> bool:
        raise NotImplementedError()

    def get_all_mods(self) -> Sequence[Mod]:
        raise NotImplementedError()
