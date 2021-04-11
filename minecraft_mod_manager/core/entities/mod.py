from __future__ import annotations
from enum import Enum
from typing import Set, Union
import re


class RepoTypes(Enum):
    unknown = "unknown"
    curse = "curse"


class ModArg:
    """Mod argument from the CLI"""

    def __init__(self, repo_type: RepoTypes, mod_name: str, alias: str) -> None:
        self.repo_type = repo_type
        """Where the mod is downloaded from"""
        self.id = mod_name
        """String identifier of the mod, often case the same as mod name"""
        self.alias = alias
        """Mod name id on the repository"""

    def __str__(self) -> str:
        return f"{self.repo_type.value}:{self.id}={self.alias}"

    def get_possible_repo_names(self) -> Set[str]:
        """Get possible repo names when the repo name hasn't been set

        Returns:
            Set[str]: Possible repo name aliases
        """
        return set(self.id)

    def __members(self):
        return (
            self.id,
            self.repo_type,
            self.alias,
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
        repo_type: RepoTypes = RepoTypes.unknown,
        alias: str = "",
        version: str = "",
        file: str = "",
        upload_time: int = 0,
    ):
        super().__init__(repo_type, id, alias)
        self.name = name
        self.version = version
        """Version of the mod"""
        self.file = file
        self.upload_time = upload_time
        """When this version of the mod was uploaded to the repository"""

    def __str__(self) -> str:
        return f"{self.name}-{self.version} ({self.id})"

    def get_possible_repo_names(self) -> Set[str]:
        possible_names: Set[str] = set()

        # Add from id
        possible_names.add(self.id.replace("_", "-"))

        # Get mod name from filename
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
            self.repo_type,
            self.alias,
            self.version,
            self.file,
            self.upload_time,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()

        return False

    def __hash__(self):
        return hash(self.__members())
