from __future__ import annotations

from enum import Enum


class RepoTypes(Enum):
    unknown = "unknown"
    curse = "curse"

    @staticmethod
    def from_name(name: str) -> RepoTypes:
        for type in RepoTypes:
            if type.value == name:
                return type
        return RepoTypes.unknown
