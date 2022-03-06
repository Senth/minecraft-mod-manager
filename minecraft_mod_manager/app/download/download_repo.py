from pathlib import Path
from typing import Dict, List, Union

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import VersionInfo


class DownloadRepo:
    def search_for_mod(self, mod: Mod) -> Dict[Sites, Site]:
        raise NotImplementedError()

    def get_versions(self, mod: Mod) -> List[VersionInfo]:
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()

    def get_mod_from_file(self, filepath: str) -> Union[Mod, None]:
        raise NotImplementedError()

    def remove_mod_file(self, filename: str) -> None:
        raise NotImplementedError()
