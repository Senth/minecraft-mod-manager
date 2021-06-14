from pathlib import Path
from typing import Dict, List, Sequence, Union

from ..app.configure.configure_repo import ConfigureRepo
from ..app.install.install_repo import InstallRepo
from ..app.show.show_repo import ShowRepo
from ..app.update.update_repo import UpdateRepo
from ..config import config
from ..core.entities.mod import Mod
from ..core.entities.sites import Site, Sites
from ..core.entities.version_info import VersionInfo
from ..core.errors.mod_not_found_exception import ModNotFoundException
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
        self.apis = (
            CurseApi(downloader),
            ModrinthApi(downloader),
        )

    def get_mod(self, id: str) -> Union[Mod, None]:
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
        return self.db.exists(id)

    def get_all_mods(self) -> Sequence[Mod]:
        return self.mods

    def remove_mod_file(self, filename: str) -> None:
        path = Path(config.dir).joinpath(filename)
        path.unlink(missing_ok=True)

    def search_for_mod(self, mod: Mod) -> Dict[Sites, Site]:
        sites: Dict[Sites, Site] = {}

        for api in self.apis:
            if mod.matches_site(api.site_name):
                # Already has an id
                if mod.sites and api.site_name in mod.sites and mod.sites[api.site_name].id:
                    Logger.verbose(f"🔍 Previously found on {api.site_name.value}")
                    return mod.sites
                try:
                    Logger.verbose(f"🔍 Searching on {api.site_name.value}...", indent=1)
                    site = api.find_mod_id(mod)
                    sites[site.name] = site
                    RepoImpl._print_found()
                except ModNotFoundException:
                    RepoImpl._print_not_found()

        if len(sites) == 0:
            raise ModNotFoundException(mod)

        return sites

    def get_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []

        for api in self.apis:
            if mod.matches_site(api.site_name):
                versions.extend(api.get_all_versions(mod))

        return versions

    def download(self, url: str, filename: str = "") -> Path:
        return Path(self.downloader.download(url, filename))

    @staticmethod
    def _print_found():
        Logger.verbose("Found", LogColors.green, indent=2)

    @staticmethod
    def _print_not_found():
        Logger.verbose("Not found", LogColors.yellow, indent=2)
