from typing import Sequence, Union

from ...core.entities.mod import Mod
from ...core.entities.version_info import VersionInfo
from ..download.download_repo import DownloadRepo


class UpdateRepo(DownloadRepo):
    def get_latest_version(self, mod: Mod) -> VersionInfo:
        raise NotImplementedError()

    def get_all_mods(self) -> Sequence[Mod]:
        raise NotImplementedError()

    def get_mod(self, id: str) -> Union[Mod, None]:
        raise NotImplementedError()

    def remove_mod_file(self, filename: str) -> None:
        raise NotImplementedError()
