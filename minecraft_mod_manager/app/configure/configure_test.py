from __future__ import unicode_literals

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod, ModArg
from ...core.entities.sites import Sites
from .configure import Configure
from .configure_repo import ConfigureRepo


@pytest.fixture
def mock_repo():
    return mock(ConfigureRepo)


def test_abort_when_mod_not_found(mock_repo):
    when(mock_repo).get_mod(...).thenReturn(None)
    configure = Configure(mock_repo)
    input = [ModArg(site=Sites.unknown, id="not-found", slug="")]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    unstub()
    assert e.type == SystemExit


def test_abort_before_updating_when_later_mod_not_found(mock_repo):
    when(mock_repo).get_mod("found").thenReturn(Mod("", ""))
    when(mock_repo).get_mod("not-found").thenReturn(None)

    configure = Configure(mock_repo)
    input = [
        ModArg(site=Sites.unknown, id="found", slug="test"),
        ModArg(site=Sites.unknown, id="not-found", slug=""),
    ]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    unstub()
    assert e.type == SystemExit


def test_mod_repo_changed(mock_repo):
    expected_update = Mod("carpet", "", site=Sites.curse)

    when(mock_repo).get_mod("carpet").thenReturn(Mod("carpet", ""))
    when(mock_repo).update_mod(expected_update)

    configure = Configure(mock_repo)
    input = [
        ModArg(site=Sites.curse, id="carpet", slug=""),
    ]

    configure.execute(input)

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_mod_alias_changed(mock_repo):
    expected_update = Mod("carpet", "", site_slug="carpet_alias")

    when(mock_repo).get_mod("carpet").thenReturn(Mod("carpet", ""))
    when(mock_repo).update_mod(expected_update)

    configure = Configure(mock_repo)
    input = [
        ModArg(site=Sites.unknown, id="carpet", slug="carpet_alias"),
    ]

    configure.execute(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
