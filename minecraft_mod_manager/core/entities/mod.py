from __future__ import annotations

import re
from typing import Dict, Set, Union

from .mod_loaders import ModLoaders
from .sites import Site, Sites


class ModArg:
    """Mod argument from the CLI"""

    def __init__(self, id: str, sites: Union[Dict[Sites, Site], None] = None) -> None:
        self.sites = sites
        """Where the mod is downloaded from"""
        self.id = id
        """String identifier of the mod, often case the same as mod name"""

    def matches_site(self, site: Sites) -> bool:
        if self.sites:
            return site in self.sites
        return True

    def get_site_slug_string(self) -> str:
        sites = ""
        if self.sites:
            for site in self.sites.values():
                if len(sites) > 0:
                    sites += ", "
                sites += site.get_configure_string()

        return sites

    def __str__(self) -> str:
        return f"{self.id}={self.get_site_slug_string()}"

    def __repr__(self) -> str:
        return str(self.__members())

    def __lt__(self, other: ModArg) -> bool:
        return self.id < other.id

    def __le__(self, other: ModArg) -> bool:
        return self.id <= other.id

    def __gt__(self, other: ModArg) -> bool:
        return self.id > other.id

    def __ge__(self, other: ModArg) -> bool:
        return self.id >= other.id

    def __members(self):
        return (
            self.id,
            self.sites,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()

        return False

    def __hash__(self) -> int:
        return hash(self.__members())


class Mod(ModArg):
    def __init__(
        self,
        id: str,
        name: str,
        sites: Union[Dict[Sites, Site], None] = None,
        version: Union[str, None] = None,
        file: Union[str, None] = None,
        upload_time: int = 0,
        mod_loader: ModLoaders = ModLoaders.unknown,
    ):
        super().__init__(id, sites)
        self.name = name
        self.version = version
        self.file = file
        self.mod_loader = mod_loader
        self.upload_time = upload_time
        """When this version of the mod was uploaded to the repository"""

    @staticmethod
    def fromModArg(mod_arg: ModArg) -> Mod:
        return Mod(mod_arg.id, mod_arg.id, mod_arg.sites)

    def __str__(self) -> str:
        return f"{self.id}-{self.version} ({self.name}) [{self.mod_loader.value}]"

    def __repr__(self) -> str:
        return str(self.__members())

    def get_possible_slugs(self) -> Set[str]:
        possible_names: Set[str] = set()

        # Add from id
        possible_names.add(self.id.replace("_", "-"))

        # Get mod name from filename
        if self.file:
            match = re.match(r"(\w+-\w+-\w+|\w+-\w+|\w+)-", self.file)

            if match and match.lastindex == 1:
                # Add basic name
                filename = match.group(1).lower().replace("_", "-")
                possible_names.add(filename)

                # Remove possible 'fabric' from the name
                without_fabric = re.sub(r"-fabric\w*|fabric\w*-", "", filename)
                possible_names.add(without_fabric)

        return possible_names

    def __members(self):
        return (
            self.id,
            self.name,
            self.sites,
            self.version,
            self.file,
            self.upload_time,
            self.mod_loader,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self):
        return hash(self.__members())
