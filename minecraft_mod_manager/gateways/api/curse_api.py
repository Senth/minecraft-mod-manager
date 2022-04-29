from typing import Any, List

from ...core.entities.mod import Mod, ModArg
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..http import Http
from .api import Api

_base_url = "https://addons-ecs.forgesvc.net/api/v2/addon"


class CurseApi(Api):
    def __init__(self, http: Http) -> None:
        super().__init__(http, Sites.curse)

    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []
        files = self.http.get(CurseApi._make_files_url(mod))
        for file in files:
            version = CurseApi._file_to_version_info(file)
            version.name = mod.name
            versions.append(version)

        return versions

    @staticmethod
    def _make_files_url(mod: Mod) -> str:
        if mod.sites:
            return f"{_base_url}/{mod.sites[Sites.curse].id}/files"
        raise RuntimeError("No site id found")

    def search_mod(self, search: str) -> List[Site]:
        mods: List[Site] = []
        json = self.http.get(CurseApi._make_search_url(search))
        for curse_mod in json:
            if "slug" in curse_mod and "id" in curse_mod:
                slug = curse_mod["slug"]
                site_id = curse_mod["id"]
                mods.append(Site(Sites.curse, str(site_id), slug))
        return mods

    @staticmethod
    def _make_search_url(search: str) -> str:
        return f"{_base_url}/search?gameId=432&sectionId=6&searchFilter={search}"

    def get_mod_info(self, site_id: str) -> Mod:
        json = self.http.get(self._make_get_mod_url(site_id))
        if json and "id" in json and "slug" in json and "name" in json:
            return Mod(
                id="",
                name=json["name"],
                sites={Sites.curse: Site(Sites.curse, str(json["id"]), json["slug"])},
            )
        raise ModNotFoundException(ModArg(site_id))

    @staticmethod
    def _make_get_mod_url(site_id: str) -> str:
        return f"{_base_url}/{site_id}"

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
