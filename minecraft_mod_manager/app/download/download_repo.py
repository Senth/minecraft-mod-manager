from pathlib import Path
from typing import List, Optional

from ...core.entities.mod import Mod
from ...core.entities.version_info import VersionInfo


class DownloadRepo:
    def get_versions(self, mod: Mod) -> List[VersionInfo]:
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()

    def get_mod_from_file(self, filepath: str) -> Optional[Mod]:
        raise NotImplementedError()

    def remove_mod_file(self, filename: str) -> None:
        raise NotImplementedError()
