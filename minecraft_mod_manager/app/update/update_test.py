from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from .update import Update
from .update_repo import UpdateRepo


@pytest.fixture
def mock_repo():
    return mock(UpdateRepo)


def test_use_all_installed_mods_when_no_mods_are_specified(mock_repo):
    mods: List[Mod] = [Mod("1", "one"), Mod("2", "two")]
    update = Update(mock_repo)
    when(mock_repo).get_all_mods().thenReturn(mods)
    when(update).find_download_and_install(...)

    update.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_call_find_download_and_install(mock_repo):
    when(mock_repo).get_all_mods().thenReturn([])
    update = Update(mock_repo)
    when(update).find_download_and_install(...)

    update.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()
