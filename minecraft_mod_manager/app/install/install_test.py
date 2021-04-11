from pathlib import Path
from ...core.entities.version_info import ReleaseTypes, VersionInfo
import pytest
from mockito import mock, expect, when, verifyNoUnwantedInteractions
from .install_repo import InstallRepo
from .install import Install
from ...core.entities.mod import ModArg
from ...core.entities.repo_types import RepoTypes
from ...core.errors.mod_not_found_exception import ModNotFoundException


@pytest.fixture
def mock_repo():
    return mock(InstallRepo)


def test_mod_not_installed_when_already_installed(mock_repo):
    when(mock_repo).is_installed(...).thenReturn(True)

    input = [ModArg(RepoTypes.unknown, "", "")]
    install = Install(mock_repo)
    install.execute(input)


def test_exit_when_mod_not_found(mock_repo):
    input = [ModArg(RepoTypes.unknown, "", "")]
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_latest_version(...).thenRaise(ModNotFoundException(input[0]))

    install = Install(mock_repo)
    with pytest.raises(SystemExit) as e:
        install.execute(input)

    assert e.type == SystemExit


def test_not_downloaded_when_later_mod_not_found(mock_repo):
    input = [
        ModArg(RepoTypes.unknown, "found", ""),
        ModArg(RepoTypes.unknown, "not-found", ""),
    ]
    version_info = VersionInfo(
        release_type=ReleaseTypes.beta,
        repo_type=RepoTypes.curse,
        name="",
        upload_time=0,
        minecraft_version="",
        download_url="",
    )
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_latest_version(input[0]).thenReturn(version_info)
    when(mock_repo).get_latest_version(input[1]).thenRaise(
        ModNotFoundException(input[0])
    )

    install = Install(mock_repo)
    with pytest.raises(SystemExit) as e:
        install.execute(input)

    assert e.type == SystemExit


def test_download_and_install_when_found(mock_repo):
    input = [ModArg(RepoTypes.unknown, "found", "")]
    version_info = VersionInfo(
        release_type=ReleaseTypes.beta,
        repo_type=RepoTypes.curse,
        name="",
        upload_time=0,
        minecraft_version="",
        download_url="",
    )
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_latest_version(...).thenReturn(version_info)
    when(mock_repo).download(...).thenReturn(Path("mod.jar"))
    when(mock_repo).insert_mod(...)

    install = Install(mock_repo)
    install.execute(input)
