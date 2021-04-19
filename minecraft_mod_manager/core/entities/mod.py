from __future__ import annotations

import re
from typing import Set, Union

from .mod_loaders import ModLoaders
from .repo_types import RepoTypes


class ModArg:
    """Mod argument from the CLI"""

    def __init__(self, repo_type: RepoTypes, id: str, repo_alias: Union[str, None]) -> None:
        self.repo_type: RepoTypes = repo_type
        """Where the mod is downloaded from"""
        self.id = id
        """String identifier of the mod, often case the same as mod name"""
        self.repo_alias = repo_alias
        """Mod name id on the repository"""

    def __str__(self) -> str:
        return f"{self.repo_type.value}:{self.id}={self.repo_alias}"

    def __members(self):
        return (
            self.id,
            self.repo_type,
            self.repo_alias,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()

        return False

    def __hash__(self):
        return hash(self.__members())


class Mod(ModArg):
    def __init__(
        self,
        id: str,
        name: str,
        repo_id: Union[str, None] = None,
        repo_type: RepoTypes = RepoTypes.unknown,
        repo_alias: Union[str, None] = None,
        version: Union[str, None] = None,
        file: Union[str, None] = None,
        upload_time: int = 0,
        mod_loader: ModLoaders = ModLoaders.unknown,
    ):
        super().__init__(repo_type, id, repo_alias)
        self.repo_id = repo_id
        self.name = name
        self.version = version
        self.file = file
        self.mod_loader = mod_loader
        self.upload_time = upload_time
        """When this version of the mod was uploaded to the repository"""

    @staticmethod
    def fromModArg(mod_arg: ModArg) -> Mod:
        return Mod(mod_arg.id, mod_arg.id, repo_type=mod_arg.repo_type, repo_alias=mod_arg.repo_alias)

    def __str__(self) -> str:
        return f"{self.id}-{self.version} ({self.name}) [{self.mod_loader}]"

    def get_possible_repo_names(self) -> Set[str]:
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
            self.repo_id,
            self.repo_type,
            self.repo_alias,
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
