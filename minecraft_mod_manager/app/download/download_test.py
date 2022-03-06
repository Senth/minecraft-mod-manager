from pathlib import Path

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_file_invalid import ModFileInvalid
from .download import Download
from .download_repo import DownloadRepo


@pytest.fixture
def mock_repo():
    return mock(DownloadRepo)


def test_download_and_install_when_found(mock_repo):
    input = [Mod("found", "")]
    version_info = VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set([ModLoaders.fabric]),
        site=Sites.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )
    when(mock_repo).search_for_mod(...).thenReturn({Sites.curse: Site(Sites.curse, "", "")})
    when(mock_repo).get_versions(...).thenReturn([version_info])
    when(mock_repo).download(...).thenReturn(Path("mod.jar"))
    when(mock_repo).get_mod_from_file(...).thenReturn(Mod("found", ""))
    when(mock_repo).update_mod(...)

    download = Download(mock_repo)
    when(download).on_version_found(...)
    download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_download_and_install_remove_downloaded_file_when_invalid_mod_file(mock_repo):
    input = [Mod("found", "")]
    version_info = VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set([ModLoaders.fabric]),
        site=Sites.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )
    when(mock_repo).search_for_mod(...).thenReturn({Sites.curse: Site(Sites.curse, "", "")})
    when(mock_repo).get_versions(...).thenReturn([version_info])
    when(mock_repo).download(...).thenReturn(Path("mod.jar"))
    when(mock_repo).get_mod_from_file(...).thenRaise(ModFileInvalid(Path("mod.jar")))
    when(mock_repo).remove_mod_file(...)

    download = Download(mock_repo)
    download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_update_mod_id_after_download(mock_repo):
    download = Download(mock_repo)

    mod_arg = Mod("dummy", "name")
    installed_mod = Mod("validid", "name", version="1.0.0")
    expected_mod = Mod(
        "validid",
        "name",
        sites={Sites.curse: Site(Sites.curse, "", "")},
        version="1.0.0",
        file="mod.jar",
    )
    version_info = VersionInfo(
        stability=Stabilities.release,
        mod_loaders={ModLoaders.fabric},
        site=Sites.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )
    when(mock_repo).search_for_mod(...).thenReturn({Sites.curse: Site(Sites.curse, "", "")})
    when(mock_repo).get_versions(...).thenReturn([version_info])
    when(mock_repo).download(...).thenReturn(Path("mod.jar"))
    when(mock_repo).update_mod(expected_mod)
    when(mock_repo).get_mod_from_file("mod.jar").thenReturn(installed_mod)
    when(download).on_version_found(...)

    download.find_download_and_install([mod_arg])

    verifyStubbedInvocationsAreUsed()
    unstub()
