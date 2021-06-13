from datetime import datetime
from typing import List, Set, Tuple, Union

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...gateways.downloader import Downloader


class Api:
    def __init__(self, downloader: Downloader, site_name: Sites) -> None:
        self.downloader = downloader
        self.site_name = site_name

    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        raise NotImplementedError()

    def find_mod_id(self, mod: Mod) -> Site:
        # Specified a slug
        if mod.sites and self.site_name in mod.sites:
            existing_site = mod.sites[self.site_name]
            if existing_site.slug:
                info = self._find_mod_id_by_slug(existing_site.slug, set([existing_site.slug]))
                if info:
                    id, slug = info
                    return Site(self.site_name, id, slug)
        # No specified slug
        else:
            possible_names = mod.get_possible_slugs()
            for possible_name in possible_names:
                info = self._find_mod_id_by_slug(possible_name, possible_names)
                if info:
                    id, slug = info
                    return Site(self.site_name, id, slug)

        raise ModNotFoundException(mod)

    def _find_mod_id_by_slug(self, search: str, possible_slugs: Set[str]) -> Union[Tuple[str, str], None]:
        raise NotImplementedError()

    @staticmethod
    def _to_epoch_time(date_string: str) -> int:
        # Has milliseconds
        date = 0
        try:
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S%z")

        return round(date.timestamp())

    @staticmethod
    def _to_mod_loaders(loaders: List[str]) -> Set[ModLoaders]:
        mod_loaders: Set[ModLoaders] = set()

        for loader in loaders:
            loader = loader.lower()
            if loader == "fabric":
                mod_loaders.add(ModLoaders.fabric)
            elif loader == "forge":
                mod_loaders.add(ModLoaders.forge)

        return mod_loaders
