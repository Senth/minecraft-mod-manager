from pathlib import Path
from typing import Any, List

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

    input = [Mod("just-some-mod-id", "")]
    mock_repo: Any
    mock_finder: Any
    download: Download
    version_info = VersionInfo(
        stability=Stabilities.release,
        mod_loaders=set([ModLoaders.fabric]),
        site=Sites.curse,
        upload_time=100,
        minecraft_versions=[],
        download_url="",
        number="1.0.0",
    )

    @staticmethod
    def set_input(input: List[Mod]):
        T.input = input


@pytest.mark.parametrize(
    "name,prepare_function",
    [
        (
            "Call on_new_version_downloaded() when found",
            lambda: (
                when(T.mock_repo).download(...).thenReturn(Path("mod.jar")),
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).get_mod_from_file(...).thenReturn(Mod("found", "")),
                when(T.mock_repo).update_mod(...),
                when(T.download).on_new_version_downloaded(...),
            ),
        ),
        (
            "Remove downloaded file when invalid mod file",
            lambda: (
                when(T.mock_repo).download(...).thenReturn(Path("mod.jar")),
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).get_mod_from_file(...).thenRaise(ModFileInvalid(Path("mod.jar"))),
                when(T.mock_repo).remove_mod_file(...),
            ),
        ),
        (
            "Update mod_id after download",
            lambda: (
                when(T.mock_repo).download(...).thenReturn(Path("mod.jar")),
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).update_mod(
                    Mod(
                        "validid",
                        "name",
                        sites={Sites.curse: Site(Sites.curse, "", "")},
                        version="1.0.0",
                        file="mod.jar",
                        upload_time=100,
                    )
                ),
                when(T.mock_repo).get_mod_from_file("mod.jar").thenReturn(Mod("validid", "name", version="1.0.0")),
                when(T.download).on_new_version_downloaded(...),
            ),
        ),
        (
            "Download dependency",
            lambda: (
                when(T.mock_repo).download(...).thenReturn(Path("mod.jar")),
                when(T.mock_repo)
                .get_versions(T.input[0])
                .thenReturn(
                    [
                        VersionInfo(
                            stability=Stabilities.release,
                            mod_loaders=set([ModLoaders.fabric]),
                            site=Sites.curse,
                            upload_time=100,
                            minecraft_versions=[],
                            download_url="",
                            dependencies={Sites.curse: ["123", "456"]},
                            filename="parent.jar",
                            number="1.0.1",
                        )
                    ]
                ),
                when(T.mock_repo)
                .get_versions(Mod("123", "123 Name", {Sites.curse: Site(Sites.curse, "", "")}))
                .thenReturn([T.version_info]),
                when(T.mock_finder).get_mod_info(Sites.curse, "123").thenReturn(Mod("123", "123 Name")),
                when(T.mock_finder).get_mod_info(Sites.curse, "456").thenReturn(None),
                when(T.mock_repo).download("", "parent.jar").thenReturn(Path("parent.jar")),
                when(T.mock_repo).get_mod_from_file("mod.jar").thenReturn(Mod("123", "123 Name")),
                when(T.mock_repo).get_mod_from_file("parent.jar").thenReturn(T.input[0]),
                when(T.mock_repo).update_mod(...),
                when(T.download).on_new_version_downloaded(...),
            ),
        ),
        (
            "Skip downloading if the upload date is same as the current version",
            lambda: (
                T.set_input([Mod("123", "", upload_time=100)]),
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.download).on_no_change(...),
            ),
        ),
        (
            "Downloading if the upload date older than the current version",
            lambda: (
                T.set_input([Mod("123", "", upload_time=200)]),
                when(T.mock_repo).download(...).thenReturn(Path("mod.jar")),
                when(T.mock_repo).get_versions(...).thenReturn([T.version_info]),
                when(T.mock_repo).get_mod_from_file(...).thenReturn(Mod("found", "", upload_time=200)),
                when(T.mock_repo).update_mod(...),
                when(T.download).on_new_version_downloaded(...),
            ),
        ),
    ],
)
def test_find_download_and_install(name, prepare_function):
    print(name)

    T.mock_repo = mock(DownloadRepo)
    T.mock_finder = mock(ModFinder)
    when(T.mock_finder).find_mod(...).thenReturn({Sites.curse: Site(Sites.curse, "", "")})
    T.download = Download(T.mock_repo, T.mock_finder)

    prepare_function()
    T.download.find_download_and_install(T.input)

    verifyStubbedInvocationsAreUsed()
    unstub()
