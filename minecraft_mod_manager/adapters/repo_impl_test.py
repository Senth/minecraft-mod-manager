from typing import List, Literal, Union

import pytest
from minecraft_mod_manager.core.utils.latest_version_finder import LatestVersionFinder
from minecraft_mod_manager.gateways.api.curse_api import CurseApi
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ..adapters.repo_impl import RepoImpl
from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..core.entities.sites import Sites
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


class TestGetLatestVersion:
    def __init__(
        self,
        name: str,
        mod: Mod,
        expected_result: Union[VersionInfo, type],
        expected_mod: Mod,
        curse_api_returns: Union[List[VersionInfo], ModNotFoundException, None] = None,
        version_finder_returns: Union[VersionInfo, Literal["None"], None] = None,
    ) -> None:
        self.name = name
        self.mod = mod
        self.expected_result = expected_result
        self.expected_mod = expected_mod
        self.curse_api_returns = curse_api_returns
        self.version_finder_returns = version_finder_returns


def mod(site: Sites = Sites.unknown) -> Mod:
    return Mod("", "", site=site)


def version(site: Sites = Sites.unknown) -> VersionInfo:
    return VersionInfo(
        stability=Stabilities.stable,
        mod_loader=ModLoaders.fabric,
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
                name="Get mod from Curse API when repo type is unspecified",
                mod=mod(),
                curse_api_returns=[version(site=Sites.curse)],
                version_finder_returns=version(site=Sites.curse),
                expected_result=version(site=Sites.curse),
                expected_mod=mod(site=Sites.curse),
            )
        ),
        (
            TestGetLatestVersion(
                name="Get mod from Curse API when repo type is curse",
                mod=mod(site=Sites.curse),
                curse_api_returns=[version(site=Sites.curse)],
                version_finder_returns=version(site=Sites.curse),
                expected_result=version(site=Sites.curse),
                expected_mod=mod(site=Sites.curse),
            )
        ),
        (
            TestGetLatestVersion(
                name="Mod not found in any API",
                mod=mod(),
                curse_api_returns=ModNotFoundException(mod()),
                expected_result=ModNotFoundException,
                expected_mod=mod(),
            )
        ),
        (
            TestGetLatestVersion(
                name="No latest version found",
                mod=mod(),
                curse_api_returns=[version(site=Sites.curse)],
                version_finder_returns="None",
                expected_result=ModNotFoundException,
                expected_mod=mod(site=Sites.curse),
            )
        ),
    ],
)
def test_get_latest_version(test: TestGetLatestVersion, repo_impl: RepoImpl):
    print(test.name)

    # Mocks Curse API
    if test.curse_api_returns:
        if type(test.curse_api_returns) == list:
            when(CurseApi).get_all_versions(...).thenReturn(test.curse_api_returns)
        elif type(test.curse_api_returns) == ModNotFoundException:
            when(CurseApi).get_all_versions(...).thenRaise(test.curse_api_returns)

    # Mocks Version Finder
    if test.version_finder_returns:
        if test.version_finder_returns == "None":
            when(LatestVersionFinder).find_latest_version(...)
        else:
            when(LatestVersionFinder).find_latest_version(...).thenReturn(test.version_finder_returns)

    try:
        if test.expected_result == ModNotFoundException:
            with pytest.raises(ModNotFoundException) as e:
                repo_impl.get_latest_version(test.mod)
            assert test.expected_result == e.type
        else:
            result = repo_impl.get_latest_version(test.mod)
            assert test.expected_result == result

        assert test.expected_mod == test.mod

    finally:
        verifyStubbedInvocationsAreUsed()
        unstub()
