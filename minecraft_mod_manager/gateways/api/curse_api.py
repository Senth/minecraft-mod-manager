from datetime import datetime
from typing import Any, List

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.repo_types import RepoTypes
from ...core.entities.version_info import ReleaseTypes, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..downloader import Downloader

_base_url = "https://addons-ecs.forgesvc.net/api/v2/addon"


class CurseApi:
    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        # Get the mod's id
        if not mod.repo_id:
            mod.repo_id = str(self._find_mod_id(mod))

        versions: List[VersionInfo] = []
        files = Downloader.get(CurseApi._make_files_url(mod))
        for file in files:
            version = CurseApi._file_to_version_info(file)
            version.name = mod.name
            versions.append(version)

        return versions

    def _find_mod_id(self, mod: Mod) -> int:
        json = Downloader.get(self._make_search_url(mod))

        for curse_mod in json:
            if "slug" in curse_mod and "id" in curse_mod:
                slug = curse_mod["slug"]
                if slug == mod.repo_alias:
                    return int(curse_mod["id"])

        raise ModNotFoundException(mod)

    @staticmethod
    def _make_search_url(mod: Mod) -> str:
        return f"{_base_url}/search?gameId=432&sectionId=6&searchFilter={mod.repo_alias}"

    @staticmethod
    def _make_files_url(mod: Mod) -> str:
        return f"{_base_url}/{mod.repo_id}/files"

    @staticmethod
    def _file_to_version_info(file_data: Any) -> VersionInfo:
        return VersionInfo(
            release_type=CurseApi._to_release_type(file_data["releaseType"]),
            mod_loader=CurseApi._to_mod_loader(file_data["gameVersion"]),
            repo_type=RepoTypes.curse,
            upload_time=CurseApi._to_epoch_time(file_data["fileDate"]),
            minecraft_versions=file_data["gameVersion"],
            download_url=file_data["downloadUrl"],
            filename=file_data["fileName"],
        )

    @staticmethod
    def _to_release_type(value: int) -> ReleaseTypes:
        if value == 1:
            return ReleaseTypes.stable
        elif value == 2:
            return ReleaseTypes.beta
        elif value == 3:
            return ReleaseTypes.alpha
        return ReleaseTypes.unknown

    @staticmethod
    def _to_epoch_time(date_string: str) -> int:
        date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
        return round(date.timestamp())

    @staticmethod
    def _to_mod_loader(game_versions: List[str]) -> ModLoaders:
        for game_version in game_versions:
            game_version = game_version.lower()
            if game_version == "fabric":
                return ModLoaders.fabric
            elif game_version == "forge":
                return ModLoaders.forge

        return ModLoaders.unknown
