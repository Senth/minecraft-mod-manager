from typing import Any, List, Set, Tuple, Union

from ...config import config
from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...gateways.downloader import Downloader
from .api import Api

_base_url = "https://api.modrinth.com/api/v1"


class ModrinthApi(Api):
    def __init__(self, downloader: Downloader) -> None:
        super().__init__(downloader, Sites.modrinth)

    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []
        json = self.downloader.get(ModrinthApi._make_versions_url(mod))
        for json_version in json:
            version = ModrinthApi._json_to_version_info(json_version)
            version.name = mod.name
            versions.append(version)

        return versions

    def _find_mod_id_by_slug(self, search: str, possible_slugs: Set[str]) -> Union[Tuple[str, str], None]:
        json = self.downloader.get(ModrinthApi._make_search_url(search))
        if "hits" not in json:
            return None

        for mod_info in json["hits"]:
            if "slug" in mod_info and "mod_id" in mod_info:
                slug = mod_info["slug"]
                for possible_slug in possible_slugs:
                    if slug == possible_slug:
                        site_id = str(mod_info["mod_id"])
                        site_id = site_id.replace("local-", "")
                        return site_id, slug
        return None

    @staticmethod
    def _make_search_url(search: str) -> str:
        filter = ""
        if config.filter.loader != ModLoaders.unknown:
            filter += f'&filters=categories="{config.filter.loader.value}"'
        if config.filter.version:
            filter += f'&version=versions="{config.filter.version}"'

        return f"{_base_url}/mod?query={search}{filter}"

    @staticmethod
    def _make_versions_url(mod: Mod) -> str:
        return f"{_base_url}/mod/{mod.sites[Sites.modrinth].id}/version"

    @staticmethod
    def _json_to_version_info(data: Any) -> VersionInfo:
        return VersionInfo(
            stability=Stabilities.from_name(data["version_type"]),
            mod_loaders=Api._to_mod_loaders(data["loaders"]),
            site=Sites.modrinth,
            upload_time=Api._to_epoch_time(data["date_published"]),
            minecraft_versions=data["game_versions"],
            download_url=data["files"][0]["url"],
            filename=data["files"][0]["filename"],
        )
