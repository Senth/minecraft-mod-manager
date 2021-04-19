from datetime import datetime
from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.repo_types import RepoTypes
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
            repo_alias="fabric-api",
            repo_type=RepoTypes.curse,
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
