from typing import Any, List, Set, Tuple, Union

from ...core.entities.mod import Mod
from ...core.entities.sites import Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ..downloader import Downloader
from .api import Api

_base_url = "https://addons-ecs.forgesvc.net/api/v2/addon"


class CurseApi(Api):
    def __init__(self, downloader: Downloader) -> None:
        super().__init__(downloader, Sites.curse)

    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []
        files = self.downloader.get(CurseApi._make_files_url(mod))
        for file in files:
            version = CurseApi._file_to_version_info(file)
            version.name = mod.name
            versions.append(version)

        return versions

    def _find_mod_id_by_slug(self, search: str, possible_slugs: Set[str]) -> Union[Tuple[str, str], None]:
        json = self.downloader.get(CurseApi._make_search_url(search))
        for curse_mod in json:
            if "slug" in curse_mod and "id" in curse_mod:
                slug = curse_mod["slug"]
                for possible_slug in possible_slugs:
                    if slug == possible_slug:
                        return str(curse_mod["id"]), slug
        return None

    @staticmethod
    def _make_search_url(search: str) -> str:
        return f"{_base_url}/search?gameId=432&sectionId=6&searchFilter={search}"

    @staticmethod
    def _make_files_url(mod: Mod) -> str:
        return f"{_base_url}/{mod.sites[Sites.curse].id}/files"

    @staticmethod
    def _file_to_version_info(file_data: Any) -> VersionInfo:
        return VersionInfo(
            stability=CurseApi._to_release_type(file_data["releaseType"]),
            mod_loaders=Api._to_mod_loaders(file_data["gameVersion"]),
            site=Sites.curse,
            upload_time=Api._to_epoch_time(file_data["fileDate"]),
            minecraft_versions=file_data["gameVersion"],
            download_url=file_data["downloadUrl"],
            filename=file_data["fileName"],
        )

    @staticmethod
    def _to_release_type(value: int) -> Stabilities:
        if value == 1:
            return Stabilities.release
        elif value == 2:
            return Stabilities.beta
        elif value == 3:
            return Stabilities.alpha
        return Stabilities.unknown
