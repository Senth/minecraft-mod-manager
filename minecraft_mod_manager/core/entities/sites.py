from __future__ import annotations

from enum import Enum


class Sites(Enum):
    unknown = "unknown"
    curse = "curse"
    modrinth = "modrinth"

    @staticmethod
    def from_name(name: str) -> Sites:
        for type in Sites:
            if type.value == name:
                return type
        return Sites.unknown
