from __future__ import unicode_literals
import pytest
from ...core.entities.mod import Mod, ModArg
from ...core.entities.repo_types import RepoTypes
from .configure_repo import ConfigureRepo
from .configure import Configure
from mockito import when, mock, expect, verifyNoUnwantedInteractions


@pytest.fixture
def mock_repo():
    return mock(ConfigureRepo)


def test_abort_when_mod_not_found(mock_repo):
    when(mock_repo).find_mod(...).thenReturn(None)
    configure = Configure(mock_repo)
    input = [ModArg(repo_type=RepoTypes.unknown, mod_name="not-found", alias="")]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    assert e.type == SystemExit


def test_abort_before_updating_when_later_mod_not_found(mock_repo):
    when(mock_repo).find_mod("found").thenReturn(Mod("", ""))
    when(mock_repo).find_mod("not-found").thenReturn(None)
    expect(mock_repo, times=0).update_mod(...).thenReturn(None)

    configure = Configure(mock_repo)
    input = [
        ModArg(repo_type=RepoTypes.unknown, mod_name="found", alias="test"),
        ModArg(repo_type=RepoTypes.unknown, mod_name="not-found", alias=""),
    ]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    assert e.type == SystemExit
    verifyNoUnwantedInteractions()


def test_mod_repo_changed(mock_repo):
    expected_update = Mod("carpet", "", repo_type=RepoTypes.curse)

    when(mock_repo).find_mod("carpet").thenReturn(Mod("carpet", ""))
    when(mock_repo).update_mod(expected_update)

    configure = Configure(mock_repo)
    input = [
        ModArg(repo_type=RepoTypes.curse, mod_name="carpet", alias=""),
    ]

    configure.execute(input)


def test_mod_alias_changed(mock_repo):
    expected_update = Mod("carpet", "", alias="carpet_alias")

    when(mock_repo).find_mod("carpet").thenReturn(Mod("carpet", ""))
    when(mock_repo).update_mod(expected_update)

    configure = Configure(mock_repo)
    input = [
        ModArg(repo_type=RepoTypes.unknown, mod_name="carpet", alias="carpet_alias"),
    ]

    configure.execute(input)
