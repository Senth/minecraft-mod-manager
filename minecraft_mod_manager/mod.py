from enum import Enum


class RepoTypes(Enum):
    curse = "curse"


class Mod:
    def __init__(self, id: str, name: str, version: str = "", file: str = ""):
        self.id = id
        """String identifier of the mod, often case the same as mod name"""
        self.repo_type = RepoTypes.curse
        """Where the mod is downloaded from"""
        self.repo_name_alias = self.id.replace("_", "-")
        """Mod name id on the repository"""
        self.name = name
        self.version = version
        """Version of the mod"""
        self.file = file
        self.upload_time = 0
        """When this version of the mod was uploaded to the repository"""

    def __str__(self) -> str:
        return f"{self.name}-{self.version} ({self.id})"

    def get_parse_url(self) -> str:
        if self.repo_type == RepoTypes.curse:
            return self._get_curse_url()

    def _get_curse_url(self) -> str:
        return (
            f"https://www.curseforge.com/minecraft/mc-mods/{self.repo_name_alias}/files"
        )
