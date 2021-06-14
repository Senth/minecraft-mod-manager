from __future__ import annotations

from enum import Enum
from typing import Union


class Site:
    def __init__(self, name: Sites, id: Union[str, None] = None, slug: Union[str, None] = None) -> None:
        self.id = id
        self.name = name
        self.slug = slug

    def get_configure_string(self) -> str:
        slug = ""
        if self.slug:
            slug = f":{self.slug}"
        return f"{self.name.value}{slug}"

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
    def all() -> str:
        all = ""
        for name in Sites:
            if len(all) > 0:
                all += "|"
            all += name.value
        return all
