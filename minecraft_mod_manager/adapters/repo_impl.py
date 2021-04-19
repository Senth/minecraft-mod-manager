from pathlib import Path
from typing import Sequence, Union

from ..app.configure.configure_repo import ConfigureRepo
from ..app.install.install_repo import InstallRepo
from ..app.show.show_repo import ShowRepo
from ..app.update.update_repo import UpdateRepo
from ..core.entities.mod import Mod, ModArg
from ..core.entities.version_info import VersionInfo
from ..gateways.downloader import Downloader
from ..gateways.jar_parser import JarParser
from ..gateways.sqlite import Sqlite


class InstalledRepo(ConfigureRepo, UpdateRepo, InstallRepo, ShowRepo):
    """Cache/Adapter between jar_parser, sqlite and the rest of the application"""

    def __init__(self, jar_parser: JarParser, sqlite: Sqlite, downloader: Downloader) -> None:
        self.db = sqlite
        self.mods = self.db.sync_with_dir(jar_parser.mods)
        self.downloader = downloader

    def get_mod(self, id: str) -> Union[Mod, None]:
        for installed_mod in self.mods:
            if installed_mod.id == id:
                return installed_mod
            elif installed_mod.repo_alias == id:
                return installed_mod

    def update_mod(self, mod: Mod) -> None:
        self.db.update_mod(mod)

    def is_installed(self, id: str) -> bool:
        return self.db.exists(id)

    def get_all_mods(self) -> Sequence[Mod]:
        return self.mods

    def get_latest_version(self, mod: ModArg) -> VersionInfo:

        # TODO check curse api
        raise NotImplementedError()

    def download(self, url: str, filename: str = "") -> Path:
        return Path(self.downloader.download(url, filename))
