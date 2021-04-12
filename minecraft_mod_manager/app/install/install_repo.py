from pathlib import Path
from typing import Union

from ...core.entities.mod import Mod, ModArg
from ...core.entities.version_info import VersionInfo


class InstallRepo:
    def is_installed(self, mod: ModArg) -> bool:
        raise NotImplementedError()

    def get_latest_version(self, mod: ModArg) -> Union[VersionInfo]:
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        raise NotImplementedError()

    def insert_mod(self, mod: Mod) -> None:
        raise NotImplementedError()
