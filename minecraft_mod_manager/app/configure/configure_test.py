from __future__ import unicode_literals

from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod, ModArg
from ...core.entities.sites import Site, Sites
from .configure import Configure
from .configure_repo import ConfigureRepo


@pytest.fixture
def mock_repo():
    return mock(ConfigureRepo)


def test_abort_when_mod_not_found(mock_repo):
    when(mock_repo).get_mod(...).thenReturn(None)
    configure = Configure(mock_repo)
    input = [ModArg("not-found")]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    unstub()
    assert e.type == SystemExit


def test_abort_before_configuring_when_later_mod_not_found(mock_repo):
    when(mock_repo).get_mod("found").thenReturn(Mod("", ""))
    when(mock_repo).get_mod("not-found").thenReturn(None)

    configure = Configure(mock_repo)
    input = [
        ModArg("found"),
        ModArg("not-found"),
    ]

    with pytest.raises(SystemExit) as e:
        configure.execute(input)

    unstub()
    assert e.type == SystemExit


@pytest.mark.parametrize(
    "name,existing,input,expected",
    [
        (
            "Set site when specified",
            Mod("carpet", ""),
            [ModArg("carpet", {Sites.modrinth: Site(Sites.modrinth)})],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
        ),
        (
            "Change sites when specified",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
            [ModArg("carpet", {Sites.curse: Site(Sites.curse)})],
            Mod("carpet", "", {Sites.curse: Site(Sites.curse)}),
        ),
        (
            "Mod sites remove when no is specified",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
            [ModArg("carpet", {})],
            Mod("carpet", "", {}),
        ),
        (
            "Keep old info if no site is specified",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
            [ModArg("carpet")],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
        ),
        (
            "Set slug when specified",
            Mod("carpet", ""),
            [ModArg("carpet", {Sites.modrinth: Site(Sites.modrinth, slug="fabric-carpet")})],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, slug="fabric-carpet")}),
        ),
        (
            "Remove slug when not specified",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, slug="fabric-carpet")}),
            [ModArg("carpet", {Sites.modrinth: Site(Sites.modrinth)})],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth)}),
        ),
        (
            "Slug updated when specified",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, slug="fabric-carpet")}),
            [ModArg("carpet", {Sites.modrinth: Site(Sites.modrinth, slug="car")})],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, slug="car")}),
        ),
        (
            "Site id is kept when changing other settings",
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, "id", slug="fabric-carpet")}),
            [ModArg("carpet", {Sites.modrinth: Site(Sites.modrinth, slug="car")})],
            Mod("carpet", "", {Sites.modrinth: Site(Sites.modrinth, "id", slug="car")}),
        ),
    ],
)
def test_configure_mod(name: str, existing: Mod, input: List[ModArg], expected: Mod, mock_repo: ConfigureRepo):
    when(mock_repo).get_mod(existing.id).thenReturn(existing)
    when(mock_repo).update_mod(expected)

    configure = Configure(mock_repo)
    configure.execute(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
