import json
from pathlib import Path

import pytest
from minecraft_mod_manager.core.entities.repo_types import RepoTypes
from minecraft_mod_manager.core.entities.version_info import ReleaseTypes, VersionInfo
from mockito import unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
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
    return Mod("carpet", "Carpet", repo_alias="carpet", repo_id="349239")


def test_find_mod_id(mod: Mod, api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)

    mod_id = api._find_mod_id(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert mod_id == int(mod.repo_id)


def test_raise_exception_when_mod_not_found(api: CurseApi, carpet_search):
    when(Downloader).get(...).thenReturn(carpet_search)

    with pytest.raises(ModNotFoundException) as e:
        api._find_mod_id(Mod("oaeu", "uu"))

    verifyStubbedInvocationsAreUsed()
    unstub

    assert e.type == ModNotFoundException


def test_get_latest_version_when_we_have_mod_id(mod: Mod, api: CurseApi, carpet_files):
    when(Downloader).get(...).thenReturn(carpet_files)
    expected = VersionInfo(
        ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Carpet",
        upload_time=0,
        minecraft_version="1.17",
        download_url="https://edge.forgecdn.net/files/3276/130/fabric-carpet-21w15a-1.4.32+v210414.jar",
        filename="fabric-carpet-21w15a-1.4.32+v210414.jar",
    )

    version_info = api.get_latest_version(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert version_info == expected
