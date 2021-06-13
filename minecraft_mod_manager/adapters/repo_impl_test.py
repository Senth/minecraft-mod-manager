from typing import Any, List, Literal, Union

import pytest
from minecraft_mod_manager.gateways.api import modrinth_api
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ..adapters.repo_impl import RepoImpl
from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..core.entities.sites import Sites
from ..core.entities.version_info import Stabilities, VersionInfo
from ..core.errors.mod_not_found_exception import ModNotFoundException
from ..core.utils.latest_version_finder import LatestVersionFinder
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


class TestGetLatestVersion:
    def __init__(
        self,
        name: str,
        mod: Mod,
        expected_result: Union[List[VersionInfo], type, None],
        curse_api_returns: Union[List[VersionInfo], ModNotFoundException, None] = None,
        modrinth_api_returns: Union[List[VersionInfo], ModNotFoundException, None] = None,
    ) -> None:
        self.name = name
        self.mod = mod
        self.expected_result = expected_result
        self.curse_api_returns = curse_api_returns
        self.modrinth_api_returns = modrinth_api_returns


def mod(site: Sites = Sites.unknown) -> Mod:
    return Mod("", "", site=site)


def version(site: Sites = Sites.unknown) -> VersionInfo:
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
        (
            TestGetLatestVersion(
                name="Get mod from Modrinth API when site type is specified",
                mod=mod(site=Sites.modrinth),
                modrinth_api_returns=[version(site=Sites.modrinth)],
                expected_result=[version(site=Sites.modrinth)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Modrinth API when site type is unspecified",
                mod=mod(),
                modrinth_api_returns=[version(site=Sites.modrinth)],
                curse_api_returns=[],
                expected_result=[version(site=Sites.modrinth)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Modrinth API when site type is unspecified and Curse returns Exception",
                mod=mod(),
                modrinth_api_returns=[version(site=Sites.modrinth)],
                curse_api_returns=ModNotFoundException(mod()),
                expected_result=[version(site=Sites.modrinth)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Curse API when site type is curse",
                mod=mod(site=Sites.curse),
                curse_api_returns=[version(site=Sites.curse)],
                expected_result=[version(site=Sites.curse)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Curse API when site type is unspecified",
                mod=mod(),
                modrinth_api_returns=[],
                curse_api_returns=[version(site=Sites.curse)],
                expected_result=[version(site=Sites.curse)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Curse API when site type is unspecified and Modrinth return exception",
                mod=mod(),
                modrinth_api_returns=ModNotFoundException(mod()),
                curse_api_returns=[version(site=Sites.curse)],
                expected_result=[version(site=Sites.curse)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Curse API when site type is curse",
                mod=mod(site=Sites.curse),
                curse_api_returns=[version(site=Sites.curse)],
                expected_result=[version(site=Sites.curse)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from all sites",
                mod=mod(),
                modrinth_api_returns=[version(site=Sites.modrinth)],
                curse_api_returns=[version(site=Sites.curse)],
                expected_result=[version(site=Sites.modrinth), version(site=Sites.curse)],
            )
        ),
        (
            TestGetLatestVersion(
                name="Mod not found in any API",
                mod=mod(),
                modrinth_api_returns=ModNotFoundException(mod()),
                curse_api_returns=ModNotFoundException(mod()),
                expected_result=ModNotFoundException,
            )
        ),
    ],
)
def test_get_latest_version(test: TestGetLatestVersion, repo_impl: RepoImpl):
    print(test.name)

    # Mocks API
    mock_get_all_versions(repo_impl.modrinth_api, test.modrinth_api_returns)
    mock_get_all_versions(repo_impl.curse_api, test.curse_api_returns)

    try:
        if test.expected_result == ModNotFoundException:
            with pytest.raises(ModNotFoundException) as e:
                repo_impl.get_versions(test.mod)
            assert test.expected_result == e.type
        else:
            result = repo_impl.get_versions(test.mod)
            assert test.expected_result == result

    finally:
        verifyStubbedInvocationsAreUsed()
        unstub()


def mock_get_all_versions(api: Any, result: Union[List[VersionInfo], ModNotFoundException, None]) -> None:
    if type(result) == list:
        when(api).get_all_versions(...).thenReturn(result)
    elif type(result) == ModNotFoundException:
        when(api).get_all_versions(...).thenRaise(result)
