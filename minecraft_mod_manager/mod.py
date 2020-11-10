from enum import Enum
from typing import List, Set
import re


class RepoTypes(Enum):
    unknown = "unknown"
    curse = "curse"


class Mod:
    def __init__(
        self,
        id: str,
        name: str,
        repo_type: RepoTypes = RepoTypes.unknown,
        repo_name_alias: str = "",
        version: str = "",
        file: str = "",
        upload_time=0,
    ):
        self.id = id
        """String identifier of the mod, often case the same as mod name"""
        self.repo_type = repo_type
        """Where the mod is downloaded from"""
        self.repo_name_alias = repo_name_alias
        """Mod name id on the repository"""
        self.name = name
        self.version = version
        """Version of the mod"""
        self.file = file
        self.upload_time = upload_time
        """When this version of the mod was uploaded to the repository"""

    def __str__(self) -> str:
        return f"{self.name}-{self.version} ({self.id})"

    def get_possible_repo_names(self) -> Set[str]:
        """Get possible repo names when the repo name hasn't been set

        Returns:
            List[str]: Possible repo name aliases
        """
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
