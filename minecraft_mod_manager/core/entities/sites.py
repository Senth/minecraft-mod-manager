from __future__ import annotations

from enum import Enum
from typing import List, Union


class Site:
    def __init__(self, name: Sites, id: Union[str, None] = None, slug: Union[str, None] = None) -> None:
        self.id = id
        self.name = name
        self.slug = slug

    def __str__(self) -> str:
        return f"Site({self.name.value}, {self.id}, {self.slug})"

    def __repr__(self) -> str:
        return str(self.__members())

    def __members(self):
        return (
            self.id,
            self.name,
            self.slug,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self) -> int:
        return hash(self.__members())


class Sites(Enum):
    curse = "curse"
    modrinth = "modrinth"

    @staticmethod
    def from_names(names: str) -> List[Sites]:
        """Get all sites from a string with comma separated names

        Args:
            names (str): Comma separated names. Invalid names are ignored.

        Returns:
            List[Sites]: All found names, empty list if names is empty
        """
        sites: List[Sites] = []
        for name in names.split(","):
            site = Sites.from_name(name)
            if site:
                sites.append(site)
        return sites

    @staticmethod
    def from_name(name: str) -> Union[Sites, None]:
        for type in Sites:
            if type.value == name:
                return type
        return None
