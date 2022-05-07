import json
from pathlib import Path
from typing import Optional

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ..http import Http
from .curse_api import CurseApi

testdata_dir = Path(__file__).parent.joinpath("testdata").joinpath("curse_api")
search_carpet_file = testdata_dir.joinpath("search_carpet.json")
files_carpet_file = testdata_dir.joinpath("files_carpet.json")
mod_info_file = testdata_dir.joinpath("mod_info.json")


@pytest.fixture
def carpet_search():
    with open(search_carpet_file) as file:
        return json.load(file)


@pytest.fixture
def carpet_files():
    with open(files_carpet_file) as file:
        return json.load(file)


@pytest.fixture
def mod_info():
    with open(mod_info_file) as file:
        return json.load(file)


@pytest.fixture
def http():
    mocked = mock(Http)
    yield mocked
    unstub()


@pytest.fixture
def api(http):
    return CurseApi(http)


site_id = "349239"


def mod(id="carpet", name="Carpet", site_slug="carpet", site_id=site_id, file: Optional[str] = None):
    return Mod(id=id, name=name, sites={Sites.curse: Site(Sites.curse, site_id, site_slug)}, file=file)


def test_search_mod(api: CurseApi, carpet_search):
    when(api.http).get(...).thenReturn(carpet_search)
    expected = [
        Site(Sites.curse, "349239", "carpet"),
        Site(Sites.curse, "361689", "carpet-stairs-mod"),
        Site(Sites.curse, "349240", "carpet-extra"),
        Site(Sites.curse, "409947", "ceiling-carpets"),
        Site(Sites.curse, "397510", "carpet-tis-addition"),
        Site(Sites.curse, "315944", "forgedcarpet"),
        Site(Sites.curse, "441529", "ivan-carpet-addition"),
        Site(Sites.curse, "229429", "weather-carpets-mod"),
        Site(Sites.curse, "443142", "carpet-without-player"),
        Site(Sites.curse, "417744", "carpet-wood"),
        Site(Sites.curse, "264320", "no-collide-carpets"),
        Site(Sites.curse, "40519", "carpet-mod"),
    ]

    actual = api.search_mod("carpet")

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual


def test_get_mod_info(api: CurseApi, mod_info):
    when(api.http).get(...).thenReturn(mod_info)
    expected = Mod(
        id="",
        name="Litematica",
        sites={Sites.curse: Site(Sites.curse, "308892", "litematica")},
    )

    actual = api.get_mod_info("123")

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual


def test_get_mod_info_not_found(api: CurseApi):
    when(api.http).get(...).thenReturn({"error": "not found"})

    with pytest.raises(ModNotFoundException):
        api.get_mod_info("123")

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_get_all_versions(api: CurseApi, carpet_files):
    when(api.http).get(...).thenReturn(carpet_files)
    expected = [
        VersionInfo(
            stability=Stabilities.beta,
            mod_loaders=set([ModLoaders.forge]),
            site=Sites.curse,
            mod_name="Carpet",
            upload_time=1585794423,
            minecraft_versions=["1.16-Snapshot", "Forge"],
            download_url="https://edge.forgecdn.net/files/2918/924/fabric-carpet-20w13b-1.3.17+v200401.jar",
            filename="fabric-carpet-20w13b-1.3.17+v200401.jar",
            dependencies={Sites.curse: ["1337", "1338"]},
            number="20w13b-1.3.17+v200401",
        ),
        VersionInfo(
            stability=Stabilities.alpha,
            mod_loaders=set([]),
            site=Sites.curse,
            mod_name="Carpet",
            upload_time=1571975688,
            minecraft_versions=["1.14.4"],
            download_url="https://edge.forgecdn.net/files/2815/968/fabric-carpet-1.14.4-1.2.0+v191024.jar",
            filename="fabric-carpet-1.14.4-1.2.0+v191024.jar",
            number="1.14.4-1.2.0+v191024",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric]),
            site=Sites.curse,
            mod_name="Carpet",
            upload_time=1618425238,
            minecraft_versions=["Fabric", "1.16.5", "1.16.4"],
            download_url="https://edge.forgecdn.net/files/3276/129/fabric-carpet-1.16.5-1.4.32+v210414.jar",
            filename="fabric-carpet-1.16.5-1.4.32+v210414.jar",
            number="1.16.5-1.4.32+v210414",
        ),
        VersionInfo(
            stability=Stabilities.release,
            mod_loaders=set([ModLoaders.fabric, ModLoaders.forge]),
            site=Sites.curse,
            mod_name="Carpet",
            upload_time=1618425279,
            minecraft_versions=["1.17", "Fabric", "Forge"],
            download_url="https://edge.forgecdn.net/files/3276/130/fabric-carpet-21w15a-1.4.32+v210414.jar",
            filename="fabric-carpet-21w15a-1.4.32+v210414.jar",
            number="21w15a-1.4.32+v210414",
        ),
    ]

    actual = api.get_all_versions(mod())

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual
