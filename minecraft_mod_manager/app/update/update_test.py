from typing import List, Union

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...config import config
from ...core.entities.mod import Mod
from ...core.entities.sites import Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...gateways.api.mod_finder import ModFinder
from .update import Update
from .update_repo import UpdateRepo


@pytest.fixture
def mock_repo():
    return mock(UpdateRepo)


@pytest.fixture
def mock_finder():
    return mock(ModFinder)


def test_use_all_installed_mods_when_no_mods_are_specified(mock_repo, mock_finder):
    mods: List[Mod] = [Mod("1", "one"), Mod("2", "two")]
    update = Update(mock_repo, mock_finder)
    when(mock_repo, mock_finder).get_all_mods().thenReturn(mods)
    when(update).find_download_and_install(...)

    update.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_call_find_download_and_install(mock_repo, mock_finder):
    when(mock_repo, mock_finder).get_all_mods().thenReturn([])
    update = Update(mock_repo, mock_finder)
    when(update).find_download_and_install(...)

    update.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()


def version_info(filename: str) -> VersionInfo:
    return VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set(),
        site=Sites.curse,
        upload_time=1,
        minecraft_versions=[],
        download_url="",
        filename=filename,
        number="1.0.0",
    )


@pytest.mark.parametrize(
    "name,old,new,pretend,expected",
    [
        (
            "Remove file when new file has been downloaded",
            "old",
            "new",
            False,
            True,
        ),
        (
            "Keep file when no new file has been downloaded",
            "old",
            "old",
            False,
            False,
        ),
        (
            "Keep old file when new filename is empty",
            "old",
            "",
            False,
            False,
        ),
        (
            "Don't remove old file when it doesn't exist",
            None,
            "new",
            False,
            False,
        ),
        (
            "Don't remove old file when it's empty",
            "",
            "new",
            False,
            False,
        ),
        (
            "Don't remove old file when --pretend is on",
            "old",
            "new",
            True,
            False,
        ),
    ],
)
def test_on_version_found(
    name: str, old: Union[str, None], new: Union[str, None], pretend: bool, expected: bool, mock_repo, mock_finder
):
    print(name)

    config.pretend = pretend
    if expected:
        when(mock_repo).remove_mod_file(old)

    update = Update(mock_repo, mock_finder)
    old_mod = Mod("", "", file=old)
    new_mod = Mod("", "", file=new)
    update.on_new_version_downloaded(old_mod, new_mod)

    config.pretend = False
    verifyStubbedInvocationsAreUsed()
    unstub()
