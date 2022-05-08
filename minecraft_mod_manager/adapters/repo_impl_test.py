from typing import Any, List, Union

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ..adapters.repo_impl import RepoImpl
from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..core.entities.sites import Site, Sites
from ..core.entities.version_info import Stabilities, VersionInfo
from ..core.errors.mod_not_found_exception import ModNotFoundException
from ..gateways.api.curse_api import CurseApi
from ..gateways.api.modrinth_api import ModrinthApi
from ..gateways.http import Http
from ..gateways.jar_parser import JarParser
from ..gateways.sqlite import Sqlite


@pytest.fixture
def jar_parser():
    mocked = mock(JarParser)
    mocked.mods = []  # type:ignore
    return mocked


@pytest.fixture
def sqlite():
    mocked = mock(Sqlite)
    when(mocked).sync_with_dir(...).thenReturn([])
    yield mocked
    unstub()


@pytest.fixture
def http():
    return mock(Http)


@pytest.fixture
def repo_impl(jar_parser, sqlite, http):
    repo_impl = RepoImpl(jar_parser, sqlite, http)
    repo_impl.apis = [CurseApi(http), ModrinthApi(http)]
    return repo_impl


def mod() -> Mod:
    return Mod("", "")


def mock_find_mod_id(api: Any, result: Any):
    if type(result) == Site:
        when(api).find_mod_id(...).thenReturn(result)
    elif type(result) == ModNotFoundException:
        when(api).find_mod_id(...).thenRaise(result)


class TestGetVersions:
    def __init__(
        self,
        name: str,
        mod: Mod,
        expected: List[VersionInfo] = [],
        curse_api_returns: Union[List[VersionInfo], None] = None,
        modrinth_api_returns: Union[List[VersionInfo], None] = None,
    ) -> None:
        self.name = name
        self.mod = mod
        self.expected = expected
        self.curse_api_returns = curse_api_returns
        self.modrinth_api_returns = modrinth_api_returns


def version(site: Sites) -> VersionInfo:
    return VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set([ModLoaders.fabric]),
        site=site,
        minecraft_versions=[],
        upload_time=0,
        download_url="",
        number="",
    )


@pytest.mark.parametrize(
    "test",
    [
        TestGetVersions(
            name="Get mod from Modrinth API when site type is specified",
            mod=Mod("", "", {Sites.modrinth: Site(Sites.modrinth)}),
            modrinth_api_returns=[version(site=Sites.modrinth)],
            expected=[version(site=Sites.modrinth)],
        ),
        TestGetVersions(
            name="Get mod from Modrinth API when site type is unspecified",
            mod=mod(),
            modrinth_api_returns=[version(site=Sites.modrinth)],
            curse_api_returns=[],
            expected=[version(site=Sites.modrinth)],
        ),
        TestGetVersions(
            name="Get mod from Curse API when site type is curse",
            mod=Mod("", "", {Sites.curse: Site(Sites.curse)}),
            curse_api_returns=[version(site=Sites.curse)],
            expected=[version(site=Sites.curse)],
        ),
        TestGetVersions(
            name="Get mod from Curse API when site type is unspecified",
            mod=mod(),
            modrinth_api_returns=[],
            curse_api_returns=[version(site=Sites.curse)],
            expected=[version(site=Sites.curse)],
        ),
        TestGetVersions(
            name="Get mod from Curse API when site type is curse",
            mod=Mod("", "", {Sites.curse: Site(Sites.curse)}),
            curse_api_returns=[version(site=Sites.curse)],
            expected=[version(site=Sites.curse)],
        ),
        TestGetVersions(
            name="Get mod from all sites",
            mod=mod(),
            modrinth_api_returns=[version(site=Sites.modrinth)],
            curse_api_returns=[version(site=Sites.curse)],
            expected=[version(site=Sites.modrinth), version(site=Sites.curse)],
        ),
        TestGetVersions(
            name="Get mods from all sites when all sites are specified",
            mod=Mod(
                "",
                "",
                sites={
                    Sites.modrinth: Site(Sites.modrinth),
                    Sites.curse: Site(Sites.curse),
                },
            ),
            modrinth_api_returns=[version(site=Sites.modrinth)],
            curse_api_returns=[version(site=Sites.curse)],
            expected=[version(site=Sites.modrinth), version(site=Sites.curse)],
        ),
        TestGetVersions(
            name="No versions found",
            mod=mod(),
            modrinth_api_returns=[],
            curse_api_returns=[],
            expected=[],
        ),
    ],
)
def test_get_versions(test: TestGetVersions, repo_impl: RepoImpl):
    print(test.name)

    # Mocks API
    mock_get_all_versions(repo_impl.apis[0], test.curse_api_returns)
    mock_get_all_versions(repo_impl.apis[1], test.modrinth_api_returns)

    result = repo_impl.get_versions(test.mod)

    assert sorted(test.expected) == sorted(result)

    verifyStubbedInvocationsAreUsed()
    unstub()


def mock_get_all_versions(api: Any, result: Union[List[VersionInfo], ModNotFoundException, None]) -> None:
    if type(result) == list:
        when(api).get_all_versions(...).thenReturn(result)


@pytest.mark.parametrize(
    "test_name,mods,input,expected",
    [
        (
            "Returns None when no mods",
            [],
            "id",
            None,
        ),
        (
            "Returns None when specified name",
            [
                Mod("id", "name", {}),
            ],
            "name",
            None,
        ),
        (
            "Returns mod when found by id",
            [
                Mod("id2", "name2", {}),
                Mod("id", "name", {}),
            ],
            "id",
            Mod("id", "name", {}),
        ),
        (
            "Returns mod when found by slug",
            [
                Mod(
                    "id",
                    "name",
                    {
                        Sites.modrinth: Site(Sites.modrinth, "utecro", "slug-modrinth"),
                        Sites.curse: Site(Sites.curse, "utso", "slug-curse"),
                    },
                ),
            ],
            "slug-curse",
            Mod(
                "id",
                "name",
                {
                    Sites.modrinth: Site(Sites.modrinth, "utecro", "slug-modrinth"),
                    Sites.curse: Site(Sites.curse, "utso", "slug-curse"),
                },
            ),
        ),
    ],
)
def test_get_mod(test_name: str, mods: List[Mod], input: str, expected: Union[Mod, None], repo_impl: RepoImpl):
    print(test_name)

    repo_impl.mods = mods
    result = repo_impl.get_mod(input)

    assert expected == result
