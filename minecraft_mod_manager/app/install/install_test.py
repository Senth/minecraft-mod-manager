import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import ModArg
from ...core.entities.repo_types import RepoTypes
from .install import Install
from .install_repo import InstallRepo


@pytest.fixture
def mock_repo():
    return mock(InstallRepo)


def test_mod_not_installed_when_already_installed(mock_repo):
    when(mock_repo).is_installed(...).thenReturn(True)

    input = [ModArg(RepoTypes.unknown, "", "")]
    install = Install(mock_repo)
    install.execute(input)

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_call_find_download_and_install(mock_repo):
    install = Install(mock_repo)
    when(install).find_download_and_install(...)
    install.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()
