from __future__ import annotations

from typing import Dict, List, Optional

from tealprint import TealPrint

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..http import Http
from .api import Api
from .modrinth_api import ModrinthApi
from .word_splitter_api import WordSplitterApi


class ModFinder:
    """Search and find mods on various sites"""

    @staticmethod
    def create(http: Http) -> ModFinder:
        return ModFinder(
            mod_apis=[ModrinthApi(http)],
            word_splitter_api=WordSplitterApi(http),
        )

    def __init__(self, mod_apis: List[Api], word_splitter_api: WordSplitterApi) -> None:
        self.apis = mod_apis
        self.word_splitter = word_splitter_api

    def find_mod(self, mod: Mod) -> Dict[Sites, Site]:
        """Find a mod. This differs from search in that it will only return found matches.
        It will also try with various search string until it finds a match.
        Throws an exception if no match is found."""

        TealPrint.info("🔍 Searching for mod", push_indent=True)

        found_sites: Dict[Sites, Site] = {}

        # Already specified a site slug
        for api in self.apis:
            if mod.sites and api.site_name in mod.sites:
                existing_site = mod.sites[api.site_name]
                if existing_site.slug:
                    TealPrint.verbose(f"🔍 Searching for {existing_site.slug} on {api.site_name}")
                    infos = api.search_mod(existing_site.slug)
                    for info in infos:
                        if info.slug == existing_site.slug:
                            TealPrint.verbose(f"🟢 Found {existing_site.slug} on {api.site_name}")
                            found_sites[api.site_name] = info
                            break

        if len(found_sites) > 0:
            TealPrint.pop_indent()
            return found_sites

        # Search by various possible slug names
        possible_names = mod.get_possible_slugs()
        for api in self.apis:
            TealPrint.verbose(f"🔍 Searching on {api.site_name}", push_indent=True)
            for possible_name in possible_names:
                TealPrint.debug(f"🔍 Search string: {possible_name}")
                infos = api.search_mod(possible_name)
                for info in infos:
                    if info.slug in possible_names:
                        TealPrint.debug(f"🟢 Found with slug: {info.slug}")
                        found_sites[api.site_name] = info
                        break
                if api.site_name in found_sites:
                    break
            TealPrint.pop_indent()

        if len(found_sites) > 0:
            TealPrint.pop_indent()
            return found_sites

        # Split search word and try again
        split_word = self.word_splitter.split_words(mod.id)
        if split_word != mod.id:
            for api in self.apis:
                TealPrint.verbose(f"🔍 Searching on {api.site_name} by splitting word: {split_word}")
                infos = api.search_mod(split_word)
                for info in infos:
                    if info.slug in possible_names:
                        TealPrint.debug(f"🟢 Found with slug: {info.slug}")
                        found_sites[api.site_name] = info
                        break

        TealPrint.pop_indent()
        if len(found_sites) > 0:
            return found_sites

        raise ModNotFoundException(mod)

    def get_mod_info(self, site: Sites, site_id: str) -> Optional[Mod]:
        for api in self.apis:
            if api.site_name == site:
                return api.get_mod_info(site_id)

        return None
