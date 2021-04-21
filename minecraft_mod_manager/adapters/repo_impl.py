from pathlib import Path
from typing import List, Sequence, Union

from ..app.configure.configure_repo import ConfigureRepo
from ..app.install.install_repo import InstallRepo
from ..app.show.show_repo import ShowRepo
from ..app.update.update_repo import UpdateRepo
from ..core.entities.mod import Mod
from ..core.entities.sites import Sites
from ..core.entities.version_info import VersionInfo
from ..core.errors.mod_not_found_exception import ModNotFoundException
from ..core.utils.latest_version_finder import LatestVersionFinder
from ..gateways.api.curse_api import CurseApi
from ..gateways.api.modrinth_api import ModrinthApi
from ..gateways.downloader import Downloader
from ..gateways.jar_parser import JarParser
from ..gateways.sqlite import Sqlite
from ..utils.logger import LogColors, Logger


class RepoImpl(ConfigureRepo, UpdateRepo, InstallRepo, ShowRepo):
    """Cache/Adapter between jar_parser, sqlite and the rest of the application"""

    def __init__(self, jar_parser: JarParser, sqlite: Sqlite, downloader: Downloader) -> None:
        self.db = sqlite
        self.mods = self.db.sync_with_dir(jar_parser.mods)
        self.downloader = downloader
        self.curse_api = CurseApi(downloader)
        self.modrinth_api = ModrinthApi(downloader)

    def get_mod(self, id: str) -> Union[Mod, None]:
        for installed_mod in self.mods:
            if installed_mod.id == id:
                return installed_mod
            elif installed_mod.site_slug == id:
                return installed_mod

    def update_mod(self, mod: Mod) -> None:
        self.db.update_mod(mod)

    def is_installed(self, id: str) -> bool:
        return self.db.exists(id)

    def get_all_mods(self) -> Sequence[Mod]:
        return self.mods

    def get_latest_version(self, mod: Mod) -> Union[VersionInfo, None]:
        versions: List[VersionInfo] = []

        # Modrinth
        if mod.site == Sites.modrinth or mod.site == Sites.unknown:
            try:
                Logger.verbose("🔍 Searching on Modrinth...", indent=1)
                versions.extend(self.modrinth_api.get_all_versions(mod))
                mod.site = Sites.modrinth
                RepoImpl._print_found()
            except ModNotFoundException:
                RepoImpl._print_not_found()

        # Curse
        if mod.site == Sites.curse or mod.site == Sites.unknown:
            try:
                Logger.verbose("🔍 Searching on CurseForge...", indent=1)
                versions.extend(self.curse_api.get_all_versions(mod))
                mod.site = Sites.curse
                RepoImpl._print_found()
            except ModNotFoundException:
                RepoImpl._print_not_found()

        if len(versions) == 0:
            raise ModNotFoundException(mod)

        return LatestVersionFinder.find_latest_version(mod, versions)

    def download(self, url: str, filename: str = "") -> Path:
        return Path(self.downloader.download(url, filename))

    @staticmethod
    def _print_found():
        Logger.verbose("Found", LogColors.green, indent=2)

    @staticmethod
    def _print_not_found():
        Logger.verbose("Not found", LogColors.yellow, indent=2)
