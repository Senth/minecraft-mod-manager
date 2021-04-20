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

    def get_latest_version(self, mod: Mod) -> VersionInfo:
        versions: List[VersionInfo] = []

        find_count = 0
        site_last = Sites.unknown

        # Modrinth
        if mod.site == Sites.modrinth or mod.site == Sites.unknown:
            try:
                versions.extend(self.modrinth_api.get_all_versions(mod))
                site_last = Sites.modrinth
                find_count += 1
            except ModNotFoundException:
                pass

        # Curse
        if mod.site == Sites.curse or mod.site == Sites.unknown:
            try:
                versions.extend(self.curse_api.get_all_versions(mod))
                site_last = Sites.curse
                find_count += 1
            except ModNotFoundException:
                pass

        # Only set site if found in one place
        if find_count == 1:
            mod.site = site_last

        version_info: Union[VersionInfo, None] = None
        if len(versions) > 0:
            version_info = LatestVersionFinder.find_latest_version(mod, versions)

        if version_info:
            return version_info
        else:
            raise ModNotFoundException(mod)

    def download(self, url: str, filename: str = "") -> Path:
        return Path(self.downloader.download(url, filename))
