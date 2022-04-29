import json
from pathlib import Path
from typing import Optional

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ..http import Http
from .modrinth_api import ModrinthApi

testdata_dir = Path(__file__).parent.joinpath("testdata").joinpath("modrinth_api")
search_result_file = testdata_dir.joinpath("search_fabric-api.json")
versions_result_file = testdata_dir.joinpath("versions_fabric-api.json")
versions_without_files_file = testdata_dir.joinpath("versions-without-files.json")


@pytest.fixture
def search_result():
    with open(search_result_file) as file:
        return json.load(file)


@pytest.fixture
def versions_result():
    with open(versions_result_file) as file:
        return json.load(file)


@pytest.fixture
def versions_without_files():
    with open(versions_without_files_file) as file:
        return json.load(file)


@pytest.fixture
def http():
    mocked = mock(Http)
    yield mocked
    unstub()


@pytest.fixture
def api(http):
    return ModrinthApi(http)


site_id = "P7dR8mSH"


def mod(id="fabric-api", name="Fabric API", site_slug="fabric-api", site_id=site_id, file: Optional[str] = None):
    return Mod(id=id, name=name, sites={Sites.modrinth: Site(Sites.modrinth, site_id, site_slug)}, file=file)


def test_search_mod(api: ModrinthApi, search_result):
    when(api.http).get(...).thenReturn(search_result)
    expected = [
        Site(Sites.modrinth, "P7dR8mSH", "fabric-api"),
        Site(Sites.modrinth, "720sJXM2", "bineclaims"),
        Site(Sites.modrinth, "iA9GjB4v", "BoxOfPlaceholders"),
        Site(Sites.modrinth, "ZfVQ3Rjs", "mealapi"),
        Site(Sites.modrinth, "MLYQ9VGP", "cardboard"),
        Site(Sites.modrinth, "meZK2DCX", "dawn"),
        Site(Sites.modrinth, "ssUbhMkL", "gravestones"),
        Site(Sites.modrinth, "BahnQObN", "chat-icon-api"),
        Site(Sites.modrinth, "oq1VV8nB", "splashesAPI"),
        Site(Sites.modrinth, "gno5mxtx", "grand-economy"),
    ]

    actual = api.search_mod("search string")

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual


def test_get_all_versions_directly_when_we_have_mod_id(api: ModrinthApi, versions_result):
    when(api.http).get(...).thenReturn(versions_result)
    expected = [
        VersionInfo(
            stability=Stabilities.beta,
            mod_loaders=set([ModLoaders.fabric]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1618769767,
            minecraft_versions=["21w16a"],
            download_url="https://cdn.modrinth.com/data/P7dR8mSH/versions/0.33.0+1.17/fabric-api-0.33.0+1.17.jar",
            filename="fabric-api-0.33.0+1.17.jar",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1618768763,
            minecraft_versions=["1.16.5"],
            download_url="https://cdn.modrinth.com/data/P7dR8mSH/versions/0.33.0+1.16/fabric-api-0.33.0+1.16.jar",
            filename="fabric-api-0.33.0+1.16.jar",
        ),
        VersionInfo(
            stability=Stabilities.alpha,
            mod_loaders=set([ModLoaders.forge]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1618429021,
            minecraft_versions=["21w15a"],
            download_url="https://cdn.modrinth.com/data/P7dR8mSH/versions/0.32.9+1.17/fabric-api-0.32.9+1.17.jar",
            filename="fabric-api-0.32.9+1.17.jar",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric, ModLoaders.forge]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1618427403,
            minecraft_versions=["1.16.5"],
            download_url="https://cdn.modrinth.com/data/P7dR8mSH/versions/0.32.9+1.16/fabric-api-0.32.9+1.16.jar",
            filename="fabric-api-0.32.9+1.16.jar",
        ),
    ]

    actual = api.get_all_versions(mod())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual


def test_get_versions_without_files(api: ModrinthApi, versions_without_files):
    when(api.http).get(...).thenReturn(versions_without_files)
    expected = [
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1638379386,
            minecraft_versions=["1.18"],
            download_url="https://cdn.modrinth.com/data/Nz0RSWrF/versions/0.2.5/lazy-language-loader-0.2.5.jar",
            filename="lazy-language-loader-0.2.5.jar",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric]),
            site=Sites.modrinth,
            name="Fabric API",
            upload_time=1638297554,
            minecraft_versions=["1.18"],
            download_url="https://cdn.modrinth.com/data/Nz0RSWrF/versions/0.2.3/lazy-language-loader-0.2.3.jar",
            filename="lazy-language-loader-0.2.3.jar",
        ),
    ]

    actual = api.get_all_versions(mod())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual
