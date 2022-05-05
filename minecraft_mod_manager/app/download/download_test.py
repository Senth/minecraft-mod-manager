from pathlib import Path
from typing import Any

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.mod_loaders import ModLoaders
from ...core.entities.sites import Site, Sites
from ...core.entities.version_info import Stabilities, VersionInfo
from ...core.errors.mod_file_invalid import ModFileInvalid
from ...gateways.api.mod_finder import ModFinder
from .download import Download
from .download_repo import DownloadRepo


class T:
    """Used for testing the Download class. And making use of default values for objects"""

    mock_repo: Any
    mock_finder: Any
    download: Download
    version_info = VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set([ModLoaders.fabric]),
        site=Sites.curse,
        upload_time=0,
        minecraft_versions=[],
        download_url="",
    )


@pytest.mark.parametrize(
    "name,prepare_function",
    [
        (
            "Call on_version_found() when found",
            lambda: (
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).get_mod_from_file(...).thenReturn(Mod("found", "")),
                when(T.mock_repo).update_mod(...),
                when(T.download).on_version_found(...),
            ),
        ),
        (
            "Remove downloaded file when invalid mod file",
            lambda: (
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).get_mod_from_file(...).thenRaise(ModFileInvalid(Path("mod.jar"))),
                when(T.mock_repo).remove_mod_file(...),
            ),
        ),
        (
            "Update mod_id after download",
            lambda: (
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).update_mod(
                    Mod(
                        "validid",
                        "name",
                        sites={Sites.curse: Site(Sites.curse, "", "")},
                        version="1.0.0",
                        file="mod.jar",
                    )
                ),
                when(T.mock_repo).get_mod_from_file("mod.jar").thenReturn(Mod("validid", "name", version="1.0.0")),
                when(T.download).on_version_found(...),
            ),
        ),
    ],
)
def test_find_download_and_install(name, prepare_function):
    print(name)

    input = [Mod("just-some-mod-id", "")]

    T.mock_repo = mock(DownloadRepo)
    when(T.mock_repo).download(...).thenReturn(Path("mod.jar"))
    T.mock_finder = mock(ModFinder)
    when(T.mock_finder).find_mod(...).thenReturn({Sites.curse: Site(Sites.curse, "", "")})
    T.download = Download(T.mock_repo, T.mock_finder)

    prepare_function()
    T.download.find_download_and_install(input)

    verifyStubbedInvocationsAreUsed()
    unstub()
