from __future__ import annotations

from enum import Enum


class ModLoaders(Enum):
    unknown = "unknown"
    fabric = "fabric"
    forge = "forge"

    @staticmethod
    def from_name(name: str) -> ModLoaders:
        return next(
            (
                mod_loader
                for mod_loader in ModLoaders
                if mod_loader.value == name.lower()
            ),
            ModLoaders.unknown,
        )
