from typing import Any, Dict, List, Union

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ..adapters.repo_impl import RepoImpl
from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..core.entities.sites import Site, Sites
from ..core.entities.version_info import Stabilities, VersionInfo
from ..core.errors.mod_not_found_exception import ModNotFoundException
from ..gateways.downloader import Downloader
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
def downloader():
    return mock(Downloader)


@pytest.fixture
def repo_impl(jar_parser, sqlite, downloader):
    return RepoImpl(jar_parser, sqlite, downloader)


def mod() -> Mod:
    return Mod("", "")


class TestSearchForMod:
    def __init__(
        self,
        name: str,
        mod: Mod,
        expected: Union[Dict[Sites, Site], type],
        curse_api_returns: Union[Site, ModNotFoundException, None] = None,
        modrinth_api_returns: Union[Site, ModNotFoundException, None] = None,
    ):
        self.name = name
        self.mod = mod
        self.expected = expected

        self.curse_api_returns = curse_api_returns
        self.modrinth_api_returns = modrinth_api_returns


@pytest.mark.parametrize(
    "test",
    [
        TestSearchForMod(
            name="Returns ModNotFoundException when not found anywhere",
            mod=mod(),
            expected=ModNotFoundException,
            curse_api_returns=ModNotFoundException(mod()),
            modrinth_api_returns=ModNotFoundException(mod()),
        ),
        TestSearchForMod(
            name="Returns site for Curse when found there",
            mod=mod(),
            expected={Sites.curse: Site(Sites.curse)},
            curse_api_returns=Site(Sites.curse),
            modrinth_api_returns=ModNotFoundException(mod()),
        ),
        TestSearchForMod(
            name="Returns site for Modrinth when found",
            mod=mod(),
            expected={Sites.modrinth: Site(Sites.modrinth)},
            curse_api_returns=ModNotFoundException(mod()),
            modrinth_api_returns=Site(Sites.modrinth),
        ),
        TestSearchForMod(
            name="Returns all sites when none is specified",
            mod=mod(),
            expected={Sites.curse: Site(Sites.curse), Sites.modrinth: Site(Sites.modrinth)},
            curse_api_returns=Site(Sites.curse),
            modrinth_api_returns=Site(Sites.modrinth),
        ),
        TestSearchForMod(
            name="Returns all sites when both are specified",
            mod=Mod("", "", sites={Sites.curse: Site(Sites.curse), Sites.modrinth: Site(Sites.modrinth)}),
            expected={Sites.curse: Site(Sites.curse), Sites.modrinth: Site(Sites.modrinth)},
            curse_api_returns=Site(Sites.curse),
            modrinth_api_returns=Site(Sites.modrinth),
        ),
        TestSearchForMod(
            name="Only calls api for the sites that have been specified",
            mod=Mod("", "", sites={Sites.curse: Site(Sites.curse)}),
            expected={Sites.curse: Site(Sites.curse)},
            curse_api_returns=Site(Sites.curse),
        ),
    ],
)
def test_search_for_mod(test: TestSearchForMod, repo_impl: RepoImpl):
    print(test.name)

    mock_find_mod_id(repo_impl.apis[0], test.curse_api_returns)
    mock_find_mod_id(repo_impl.apis[1], test.modrinth_api_returns)

    if test.expected == ModNotFoundException:
        with pytest.raises(ModNotFoundException) as e:
            repo_impl.search_for_mod(test.mod)
        assert test.expected == e.type
    else:
        result = repo_impl.search_for_mod(test.mod)
        assert test.expected == result

    verifyStubbedInvocationsAreUsed()
    unstub()


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
