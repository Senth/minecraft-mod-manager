from ...core.entities.mod import Mod
from ...core.entities.version_info import ReleaseTypes, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..downloader import Downloader

_base_url = "https://addons-ecs.forgesvc.net/api/v2/addon/"


class CurseApi:
    def __init__(self) -> None:
        pass

    def get_latest_version(self, mod: Mod) -> VersionInfo:
        # TODO we already have the repo id, use that to get files

        raise NotImplementedError()

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
        return f"{_base_url}search?gameId=432&sectionId=6&searchFilter={mod.repo_alias}"

    @staticmethod
    def _to_release_type(value: int) -> ReleaseTypes:
        if value == 1:
            return ReleaseTypes.stable
        elif value == 2:
            return ReleaseTypes.beta
        elif value == 3:
            return ReleaseTypes.alpha
        return ReleaseTypes.unknown
