from pathlib import Path

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
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
    when(mock_repo).update_mod(...)

    download = Download(mock_repo)
    when(download).on_version_found(...)
    download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
