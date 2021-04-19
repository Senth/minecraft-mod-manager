from pathlib import Path

from ...core.entities.mod import Mod
from ...core.entities.version_info import VersionInfo


class DownloadRepo:
    def get_latest_version(self, mod: Mod) -> VersionInfo:
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()
