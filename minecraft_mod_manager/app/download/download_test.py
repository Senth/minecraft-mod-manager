from pathlib import Path

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from .download import Download
from .download_repo import DownloadRepo


@pytest.fixture
def mock_repo():
    return mock(DownloadRepo)


def test_download_and_install_when_found(mock_repo):
    input = [Mod("found", "")]
    version_info = VersionInfo(
        stability=Stabilities.beta,
        mod_loaders=set([ModLoaders.fabric]),
        site=Sites.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )
    when(mock_repo).get_latest_version(...).thenReturn(version_info)
    when(mock_repo).download(...).thenReturn(Path("mod.jar"))
    when(mock_repo).update_mod(...)

    download = Download(mock_repo, "")
    download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
