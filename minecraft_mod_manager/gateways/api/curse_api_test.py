import json
from pathlib import Path

import pytest
from mockito import unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
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
def api():
    return CurseApi()


@pytest.fixture
def mod():
    return Mod("carpet", "Carpet", site_alias="carpet", site_id="349239")


def test_find_mod_id(mod: Mod, api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)

    mod_id = api._find_mod_id(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert mod.site_id
    assert mod_id == int(mod.site_id)


def test_find_mod_id_from_filename_without_repo_alias(mod: Mod, api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn("[]")
    when(Downloader).get(
        "https://addons-ecs.forgesvc.net/api/v2/addon/search?gameId=432&sectionId=6&searchFilter=carpet"
    ).thenReturn(carpet_search)
    mod.site_alias = None
    mod.id = "carput-fail"
    mod.file = "fabric-carpet-1.14.4-1.2.0+v191024.jar"

    mod_id = api._find_mod_id(mod)

    unstub()

    assert mod.site_id
    assert mod_id == int(mod.site_id)


def test_find_mod_id_from_filename_in_other_search_without_repo_alias(mod: Mod, api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)
    mod.site_alias = None
    mod.id = "carput-fail"
    mod.file = "fabric-carpet-1.14.4-1.2.0+v191024.jar"

    mod_id = api._find_mod_id(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert mod.site_id
    assert mod_id == int(mod.site_id)


def test_find_mod_id_from_id_without_repo_alias(mod: Mod, api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)
    mod.site_alias = None

    mod_id = api._find_mod_id(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert mod.site_id
    assert mod_id == int(mod.site_id)


def test_raise_exception_when_mod_not_found(api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)

    with pytest.raises(ModNotFoundException) as e:
        api._find_mod_id(Mod("oaeu", "uu"))

    verifyStubbedInvocationsAreUsed()
    unstub

    assert e.type == ModNotFoundException


def test_get_all_versions_directly_when_we_have_mod_id(mod: Mod, api: CurseApi, carpet_files):
    when(Downloader).get(...).thenReturn(carpet_files)
    1585794422.687, 1571975688.237, 1618425238.09, 1618425279.417
    expected = [
        VersionInfo(
            stability=Stabilities.beta,
            mod_loader=ModLoaders.forge,
            site=Sites.curse,
            name="Carpet",
            upload_time=1585794423,
            minecraft_versions=["1.16-Snapshot", "Forge"],
            download_url="https://edge.forgecdn.net/files/2918/924/fabric-carpet-20w13b-1.3.17+v200401.jar",
            filename="fabric-carpet-20w13b-1.3.17+v200401.jar",
        ),
        VersionInfo(
            stability=Stabilities.alpha,
            mod_loader=ModLoaders.unknown,
            site=Sites.curse,
            name="Carpet",
            upload_time=1571975688,
            minecraft_versions=["1.14.4"],
            download_url="https://edge.forgecdn.net/files/2815/968/fabric-carpet-1.14.4-1.2.0+v191024.jar",
            filename="fabric-carpet-1.14.4-1.2.0+v191024.jar",
        ),
        VersionInfo(
            stability=Stabilities.stable,
            mod_loader=ModLoaders.fabric,
            site=Sites.curse,
            name="Carpet",
            upload_time=1618425238,
            minecraft_versions=["Fabric", "1.16.5", "1.16.4"],
            download_url="https://edge.forgecdn.net/files/3276/129/fabric-carpet-1.16.5-1.4.32+v210414.jar",
            filename="fabric-carpet-1.16.5-1.4.32+v210414.jar",
        ),
        VersionInfo(
            stability=Stabilities.stable,
            mod_loader=ModLoaders.fabric,
            site=Sites.curse,
            name="Carpet",
            upload_time=1618425279,
            minecraft_versions=["1.17", "Fabric"],
            download_url="https://edge.forgecdn.net/files/3276/130/fabric-carpet-21w15a-1.4.32+v210414.jar",
            filename="fabric-carpet-21w15a-1.4.32+v210414.jar",
        ),
    ]

    versions = api.get_all_versions(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert versions == expected
