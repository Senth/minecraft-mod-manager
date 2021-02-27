from __future__ import annotations
from enum import Enum
from typing import Set, Union
import re


class RepoTypes(Enum):
    unknown = "unknown"
    curse = "curse"


class ModArg:
    """Mod argument from the CLI"""

    def __init__(self, repo_type: RepoTypes, mod_name: str, name_in_repo: str) -> None:
        self.repo_type = repo_type
        """Where the mod is downloaded from"""
        self.id = mod_name
        """String identifier of the mod, often case the same as mod name"""
        self.name_in_repo = name_in_repo
        """Mod name id on the repository"""

    def __str__(self) -> str:
        return f"{self.repo_type.value}:{self.id}={self.name_in_repo}"

    def get_possible_repo_names(self) -> Set[str]:
        """Get possible repo names when the repo name hasn't been set

        Returns:
            Set[str]: Possible repo name aliases
        """
        return set(self.id)


class Mod(ModArg):
    def __init__(
        self,
        id: str,
        name: str,
        repo_type: RepoTypes = RepoTypes.unknown,
        name_in_repo: str = "",
        version: str = "",
        file: str = "",
        upload_time=0,
    ):
        super().__init__(repo_type, id, name_in_repo)
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
