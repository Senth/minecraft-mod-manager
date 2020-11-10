from enum import Enum


class ReleaseTypes(Enum):
    stable = "stable"
    beta = "beta"
    alpha = "alpha"
    invalid = "invalid"


class VersionInfo:
    def __init__(
        self,
        release_type: ReleaseTypes,
        name: str,
        upload_time: int,
        minecraft_version: str,
        download_url: str,
        filename: str = "",
    ) -> None:
        self.release_type = release_type
        self.name = name
        self.upload_time = upload_time
        self.minecraft_version = minecraft_version
        self.download_url = download_url
        self.filename = filename

    def __str__(self) -> str:
        return f"{self.name} for {self.minecraft_version}, uploaded {self.upload_time}"
