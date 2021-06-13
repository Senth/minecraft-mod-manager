import json
from pathlib import Path
from typing import Union

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...gateways.downloader import Downloader
from .modrinth_api import ModrinthApi

search_result_file = Path("fixtures").joinpath("modrinth_api").joinpath("search_fabric-api.json")
versions_result_file = Path("fixtures").joinpath("modrinth_api").joinpath("versions_fabric-api.json")


@pytest.fixture
def search_result():
    with open(search_result_file) as file:
        return json.load(file)


@pytest.fixture
def versions_result():
    with open(versions_result_file) as file:
        return json.load(file)


@pytest.fixture
def downloader():
    mocked = mock(Downloader)
    yield mocked
    unstub()


@pytest.fixture
def api(downloader):
    return ModrinthApi(downloader)


site_id = "P7dR8mSH"


def mod(id="fabric-api", name="Fabric API", site_slug="fabric-api", site_id=site_id, file: Union[str, None] = None):
    return Mod(id=id, name=name, sites={Sites.modrinth: Site(Sites.modrinth, site_id, site_slug)}, file=file)


@pytest.mark.parametrize(
    "name,mod,expected",
    [
        (
            "Find site id by slug",
            mod(),
            (site_id, "fabric-api"),
        ),
        (
            "Find site id by id",
            mod(site_id=None),
            (site_id, "fabric-api"),
        ),
        (
            "Find site id from filename",
            mod(id="invalid", site_slug=None, file="fabric-api-1.14.4-1.2.0+v191024.jar"),
            (site_id, "fabric-api"),
        ),
        (
            "Site id not found",
            mod(id="invalid", site_slug=None),
            None,
        ),
    ],
)
def test_find_mod_id_by_slug(name, mod: Mod, expected, api: ModrinthApi, search_result):
    print(name)
    when(api.downloader).get(...).thenReturn(search_result)

    result = api._find_mod_id_by_slug("", mod.get_possible_slugs())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == result


def test_get_all_versions_directly_when_we_have_mod_id(api: ModrinthApi, versions_result):
    when(api.downloader).get(...).thenReturn(versions_result)
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

    versions = api.get_all_versions(mod())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == versions
