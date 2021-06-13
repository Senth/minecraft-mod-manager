from datetime import datetime
from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from .show import Show
from .show_repo import ShowRepo


@pytest.fixture
def installed_mods():
    mods: List[Mod] = [
        Mod(
            id="carpet",
            name="Carpet",
        ),
        Mod(
            id="fabric_api",
            name="Fabric API",
            sites={Sites.curse: Site(Sites.curse, "56ey55o", "fabric-api")},
        ),
        Mod(
            id="jei",
            name="Just Enough Items",
            sites={Sites.curse: Site(Sites.curse, "56ey55o")},
        ),
        Mod(
            id="sodium",
            name="Sodium",
            upload_time=int(datetime(2021, 3, 16).timestamp()),
        ),
    ]
    return mods


@pytest.fixture
def repo(installed_mods):
    mock_repo = mock(ShowRepo)
    when(mock_repo).get_all_mods(...).thenReturn(installed_mods)
    yield mock_repo
    unstub()


@pytest.fixture
def show(repo):
    return Show(repo)


def test_execute(show: Show):
    show.execute()
    verifyStubbedInvocationsAreUsed()
