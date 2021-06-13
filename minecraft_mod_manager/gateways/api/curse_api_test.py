import json
from pathlib import Path
from typing import Union

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ..downloader import Downloader
from .curse_api import CurseApi

search_carpet_file = Path("fixtures").joinpath("curse_api").joinpath("search_carpet.json")
files_carpet_file = Path("fixtures").joinpath("curse_api").joinpath("files_carpet.json")


@pytest.fixture
def carpet_search():
    with open(search_carpet_file) as file:
        return json.load(file)


@pytest.fixture
def carpet_files():
    with open(files_carpet_file) as file:
        return json.load(file)


@pytest.fixture
def downloader():
    mocked = mock(Downloader)
    yield mocked
    unstub()


@pytest.fixture
def api(downloader):
    return CurseApi(downloader)


site_id = "349239"


def mod(id="carpet", name="Carpet", site_slug="carpet", site_id=site_id, file: Union[str, None] = None):
    return Mod(id=id, name=name, sites={Sites.curse: Site(Sites.curse, site_id, site_slug)}, file=file)


@pytest.mark.parametrize(
    "name,mod,expected",
    [
        (
            "Find site id by slug",
            mod(),
            (site_id, "carpet"),
        ),
        (
            "Find site id by id",
            mod(site_id=None),
            (site_id, "carpet"),
        ),
        (
            "Find site id from filename",
            mod(id="carput-fail", site_slug=None, file="fabric-carpet-1.14.4-1.2.0+v191024.jar"),
            (site_id, "carpet"),
        ),
        (
            "Site id not found",
            mod(id="crash", site_slug=None),
            None,
        ),
    ],
)
def test_find_mod_id_by_slug(name, mod: Mod, expected, api: CurseApi, carpet_search):
    print(name)
    when(api.downloader).get(...).thenReturn(carpet_search)

    result = api._find_mod_id_by_slug("", mod.get_possible_slugs())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == result


def test_get_all_versions_directly_when_we_have_mod_id(api: CurseApi, carpet_files):
    when(api.downloader).get(...).thenReturn(carpet_files)
    expected = [
        VersionInfo(
            stability=Stabilities.beta,
            mod_loaders=set([ModLoaders.forge]),
            site=Sites.curse,
            name="Carpet",
            upload_time=1585794423,
            minecraft_versions=["1.16-Snapshot", "Forge"],
            download_url="https://edge.forgecdn.net/files/2918/924/fabric-carpet-20w13b-1.3.17+v200401.jar",
            filename="fabric-carpet-20w13b-1.3.17+v200401.jar",
        ),
        VersionInfo(
            stability=Stabilities.alpha,
            mod_loaders=set([]),
            site=Sites.curse,
            name="Carpet",
            upload_time=1571975688,
            minecraft_versions=["1.14.4"],
            download_url="https://edge.forgecdn.net/files/2815/968/fabric-carpet-1.14.4-1.2.0+v191024.jar",
            filename="fabric-carpet-1.14.4-1.2.0+v191024.jar",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric]),
            site=Sites.curse,
            name="Carpet",
            upload_time=1618425238,
            minecraft_versions=["Fabric", "1.16.5", "1.16.4"],
            download_url="https://edge.forgecdn.net/files/3276/129/fabric-carpet-1.16.5-1.4.32+v210414.jar",
            filename="fabric-carpet-1.16.5-1.4.32+v210414.jar",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric, ModLoaders.forge]),
            site=Sites.curse,
            name="Carpet",
            upload_time=1618425279,
            minecraft_versions=["1.17", "Fabric", "Forge"],
            download_url="https://edge.forgecdn.net/files/3276/130/fabric-carpet-21w15a-1.4.32+v210414.jar",
            filename="fabric-carpet-21w15a-1.4.32+v210414.jar",
        ),
    ]

    versions = api.get_all_versions(mod())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert versions == expected
