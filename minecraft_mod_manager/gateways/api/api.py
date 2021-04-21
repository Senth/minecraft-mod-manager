from datetime import datetime
from typing import List, Set, Tuple, Union

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...gateways.downloader import Downloader


class Api:
    def __init__(self, downloader: Downloader) -> None:
        self.downloader = downloader

    def _find_mod_id(self, mod: Mod) -> str:
        if mod.site_slug:
            version = self._find_mod_id_by_slug(mod.site_slug, set([mod.site_slug]))
            if version:
                return version[0]
        else:
            possible_names = mod.get_possible_slugs()
            for possible_name in possible_names:
                version_slug = self._find_mod_id_by_slug(possible_name, possible_names)
                if version_slug:
                    version, slug = version_slug
                    mod.site_slug = slug
                    return version

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
            pass

        if date == 0:
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
