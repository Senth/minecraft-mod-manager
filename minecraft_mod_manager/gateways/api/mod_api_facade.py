from typing import Dict, List

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from ...core.errors.mod_not_found_exception import ModNotFoundException
from .api import Api
from .word_splitter_api import WordSplitterApi


class ModApiFacade:
    """Search and find mods on various sites"""

    def __init__(self, mod_apis: List[Api], word_splitter_api: WordSplitterApi) -> None:
        self.apis = mod_apis
        self.word_splitter = word_splitter_api

    def find_mod(self, mod: Mod) -> Dict[Sites, Site]:
        """Find a mod. This differs from search in that it will only return found matches.
        It will also try with various search string until it finds a match.
        Throws an exception if no match is found."""

        found_sites: Dict[Sites, Site] = {}

        # Already specified a site slug
        for api in self.apis:
            if mod.sites and api.site_name in mod.sites:
                existing_site = mod.sites[api.site_name]
                if existing_site.slug:
                    infos = api.search_mod(existing_site.slug)
                    for info in infos:
                        if info.slug == existing_site.slug:
                            found_sites[api.site_name] = info
                            break

        if len(found_sites) > 0:
            return found_sites

        # Search by various possible slug names
        possible_names = mod.get_possible_slugs()
        for api in self.apis:
            for possible_name in possible_names:
                infos = api.search_mod(possible_name)
                for info in infos:
                    if info.slug in possible_names:
                        found_sites[api.site_name] = info
                        break
                if api.site_name in found_sites:
                    break

        # Split search word and try again
        split_word = self.word_splitter.split_words(mod.id)
        for api in self.apis:
            infos = api.search_mod(split_word)
            for info in infos:
                if info.slug in possible_names:
                    found_sites[api.site_name] = info
                    break

        raise ModNotFoundException(mod)
