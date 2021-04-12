import pytest
from mockito import mock, when

from ...core.entities.mod import ModArg
from ...core.entities.repo_types import RepoTypes
from ...core.entities.version_info import ReleaseTypes, VersionInfo
from ...core.errors.mod_not_found_exception import ModNotFoundException
from .update import Update
from .update_repo import UpdateRepo


@pytest.fixture
def mock_repo():
    return mock(UpdateRepo)


def test_exit_when_mod_not_found(mock_repo):
    input = [ModArg(RepoTypes.unknown, "", "")]
    when(mock_repo).get_latest_version(...).thenRaise(ModNotFoundException(input[0]))

    install = Update(mock_repo)
    with pytest.raises(SystemExit) as e:
        install.execute(input)

    assert e.type == SystemExit
