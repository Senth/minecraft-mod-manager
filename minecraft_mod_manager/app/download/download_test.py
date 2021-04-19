from pathlib import Path
from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.repo_types import RepoTypes
from ...core.entities.version_info import ReleaseTypes, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from .download import Download
from .download_repo import DownloadRepo


@pytest.fixture
def mock_repo():
    return mock(DownloadRepo)


def test_exit_when_mod_not_found(mock_repo):
    input = [Mod("", "")]
    when(mock_repo).get_latest_version(...).thenRaise(ModNotFoundException(input[0]))

    download = Download(mock_repo, "")
    with pytest.raises(SystemExit) as e:
        download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
    assert e.type == SystemExit


def test_exit_when_later_mod_not_found(mock_repo):
    input = [
        Mod("found", ""),
        Mod("not-found", ""),
    ]
    version_info = VersionInfo(
        release_type=ReleaseTypes.beta,
        mod_loader=ModLoaders.fabric,
        repo_type=RepoTypes.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )
    when(mock_repo).get_latest_version(input[0]).thenReturn(version_info)
    when(mock_repo).get_latest_version(input[1]).thenRaise(ModNotFoundException(input[0]))

    download = Download(mock_repo, "")
    with pytest.raises(SystemExit) as e:
        download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
    assert e.type == SystemExit


def test_download_and_install_when_found(mock_repo):
    input = [Mod("found", "")]
    version_info = VersionInfo(
        release_type=ReleaseTypes.beta,
        mod_loader=ModLoaders.fabric,
        repo_type=RepoTypes.curse,
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
