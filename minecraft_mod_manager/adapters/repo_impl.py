from pathlib import Path
from typing import List, Optional, Sequence

from tealprint import TealPrint

from ..app.configure.configure_repo import ConfigureRepo
from ..app.install.install_repo import InstallRepo
from ..app.show.show_repo import ShowRepo
from ..app.update.update_repo import UpdateRepo
from ..config import config
from ..core.entities.mod import Mod
from ..core.entities.version_info import VersionInfo
from ..gateways.api.api import Api
from ..gateways.api.modrinth_api import ModrinthApi
from ..gateways.http import Http
from ..gateways.jar_parser import JarParser
from ..gateways.sqlite import Sqlite
from ..utils.log_colors import LogColors


class RepoImpl(ConfigureRepo, UpdateRepo, InstallRepo, ShowRepo):
    """Cache/Adapter between jar_parser, sqlite and the rest of the application"""

    def __init__(self, jar_parser: JarParser, sqlite: Sqlite, http: Http) -> None:
        self.db = sqlite
        self.jar_parser = jar_parser
        self.mods = self.db.sync_with_dir(jar_parser.mods)
        self.http = http
        self.apis: List[Api] = [
            ModrinthApi(http),
        ]

    def get_mod(self, id: str) -> Optional[Mod]:
        for installed_mod in self.mods:
            if installed_mod.id == id:
                return installed_mod
            elif installed_mod.sites:
                for site in installed_mod.sites.values():
                    if site.slug == id:
                        return installed_mod
        return None

    def update_mod(self, mod: Mod) -> None:
        self.db.update_mod(mod)

    def is_installed(self, id: str) -> bool:
        for mod in self.mods:
            if mod.id == id:
                return True
            elif mod.sites:
                for site in mod.sites.values():
                    if site.slug == id:
                        return True
        return False

    def get_all_mods(self) -> Sequence[Mod]:
        return self.mods

    def get_mod_from_file(self, filepath: str) -> Optional[Mod]:
        return self.jar_parser.get_mod(filepath)

    def remove_mod_file(self, filename: str) -> None:
        path = Path(config.dir).joinpath(filename)
        path.unlink(missing_ok=True)

    def get_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []

        for api in self.apis:
            if mod.matches_site(api.site_name):
                versions.extend(api.get_all_versions(mod))

        return versions

    def download(self, url: str, filename: str = "") -> Path:
        return Path(self.http.download(url, filename))

    @staticmethod
    def _print_found():
        TealPrint.verbose("Found", color=LogColors.found)

    @staticmethod
    def _print_not_found():
        TealPrint.verbose("Not found", color=LogColors.not_found)
