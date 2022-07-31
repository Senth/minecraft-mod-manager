from enum import Enum
from typing import Any, Dict, List, Optional

from tealprint import TealPrint

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..http import Http
from .api import Api

_base_url = "https://api.modrinth.com/api/v1"


class DependencyTypes(Enum):
    required = "required"
    optional = "optional"
    incompatible = "incompatible"


class ModrinthApi(Api):
    def __init__(self, http: Http) -> None:
        super().__init__(http, Sites.modrinth)

    def get_all_versions(self, mod: Mod) -> List[VersionInfo]:
        versions: List[VersionInfo] = []
        json = self.http.get(ModrinthApi._make_versions_url(mod))
        for json_version in json:
            try:
                version = ModrinthApi._json_to_version_info(json_version)
                version.dependencies = self._find_dependencies_for_version(json_version)
                version.name = mod.name
                versions.append(version)
            except IndexError:
                # Skip this version
                pass

        return versions

    @staticmethod
    def _make_versions_url(mod: Mod) -> str:
        if Sites.modrinth in mod.sites:
            return f"{_base_url}/mod/{mod.sites[Sites.modrinth].id}/version"
        raise RuntimeError("No site id found")

    def search_mod(self, search: str) -> List[Site]:
        sites: List[Site] = []

        # Search by query
        mods = self._search_mod(search)

        # Get by mod slug
        try:
            mod = self.get_mod_info(search)
            mods.append(mod)
        except ModNotFoundException:
            # Not found by slug
            pass

        # Convert to site
        for mod in mods:
            sites.append(mod.sites[Sites.modrinth])

        return sites

    def _search_mod(self, search: str) -> List[Mod]:
        mods: List[Mod] = []
        json = self.http.get(ModrinthApi._make_search_url(search))
        if "hits" in json:
            for mod_info in json["hits"]:
                if {"slug", "mod_id", "title"}.issubset(mod_info):
                    slug = mod_info["slug"]
                    site_id = str(mod_info["mod_id"])
                    site_id = site_id.replace("local-", "")
                    name = mod_info["title"]
                    mods.append(Mod(id="", name=name, sites={Sites.modrinth: Site(Sites.modrinth, site_id, slug)}))

        return mods

    @staticmethod
    def _make_search_url(search: str) -> str:
        filter = ""
        if config.filter.loader != ModLoaders.unknown:
            filter += f'&filters=categories="{config.filter.loader.value}"'
        if config.filter.version:
            filter += f'&version=versions="{config.filter.version}"'

        return f"{_base_url}/mod?query={search}{filter}"

    def get_mod_info(self, site_id: str) -> Mod:
        json = self.http.get(f"{_base_url}/mod/{site_id}")
        if {"id", "slug", "title"}.issubset(json):
            return Mod(
                id="",
                name=json["title"],
                sites={Sites.modrinth: Site(Sites.modrinth, str(json["id"]), json["slug"])},
            )
        raise ModNotFoundException(ModArg(site_id))

    @staticmethod
    def _json_to_version_info(data: Any) -> VersionInfo:
        return VersionInfo(
            stability=Stabilities.from_name(data["version_type"]),
            mod_loaders=Api._to_mod_loaders(data["loaders"]),
            site=Sites.modrinth,
            upload_time=Api._to_epoch_time(data["date_published"]),
            minecraft_versions=data["game_versions"],
            number=data["version_number"],
            download_url=data["files"][0]["url"],
            filename=data["files"][0]["filename"],
        )

    def _find_dependencies_for_version(self, json_version: Any) -> Dict[Sites, List[str]]:
        dependencyVersions: List[str] = []
        dependencyProjects: List[str] = []

        for dependency in json_version["dependencies"]:
            if dependency["dependency_type"] == DependencyTypes.required.value:
                project_id = dependency["project_id"]
                version_id = dependency["version_id"]
                if project_id:
                    dependencyProjects.append(project_id)
                elif version_id:
                    dependencyVersions.append(version_id)
                else:
                    TealPrint.debug(f"No project or version id found for dependency, {dependency}")

        # Get the actual project id from the version id
        for version_id in dependencyVersions:
            project_id = self._version_id_to_mod_id(version_id)
            if project_id:
                dependencyProjects.append(project_id)

        dependencyMap: Dict[Sites, List[str]] = {}
        if dependencyProjects:
            dependencyMap[Sites.modrinth] = dependencyProjects

        return dependencyMap

    def _version_id_to_mod_id(self, version_id: str) -> Optional[str]:
        json = self.http.get(f"{_base_url}/version/{version_id}")
        if json and "mod_id" in json:
            return str(json["mod_id"])
        return ""
