from typing import Sequence, Union

from ...core.entities.mod import Mod
from ..download.download_repo import DownloadRepo


class InstallRepo(DownloadRepo):
    def is_installed(self, id: str) -> bool:
        raise NotImplementedError()

    def get_all_mods(self) -> Sequence[Mod]:
        raise NotImplementedError()

    def get_mod_from_file(self, filepath: str) -> Union[Mod, None]:
        raise NotImplementedError()
