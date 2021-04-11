from enum import Enum
from .repo_types import RepoTypes


class ReleaseTypes(Enum):
    stable = "stable"
    beta = "beta"
    alpha = "alpha"
    invalid = "invalid"


class VersionInfo:
    def __init__(
        self,
        release_type: ReleaseTypes,
        repo_type: RepoTypes,
        name: str,
        upload_time: int,
        minecraft_version: str,
        download_url: str,
        filename: str = "",
    ) -> None:
        self.release_type = release_type
        self.repo_type = repo_type
        self.name = name
        self.upload_time = upload_time
        self.minecraft_version = minecraft_version
        self.download_url = download_url
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.name} for {self.minecraft_version}, uploaded {self.upload_time}"

    def __members(self):
        return (
            self.release_type,
            self.repo_type,
            self.name,
            self.upload_time,
            self.minecraft_version,
            self.download_url,
            self.filename,
        )

    def __eq__(self, other) -> bool:
        if type(other) is type(self):
            return self.__members() == other.__members()
        return False

    def __hash__(self):
        return hash(self.__members())
