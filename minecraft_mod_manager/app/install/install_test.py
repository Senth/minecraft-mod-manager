import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod, ModArg
from ...core.entities.mod_loaders import ModLoaders
from .install import Install
from .install_repo import InstallRepo


@pytest.fixture
def mock_repo():
    return mock(InstallRepo)


def test_mod_not_installed_when_already_installed(mock_repo):
    when(mock_repo).is_installed(...).thenReturn(True)
    when(mock_repo).get_all_mods(...).thenReturn([])

    input = [ModArg("")]
    install = Install(mock_repo)
    install.execute(input)

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_call_find_download_and_install(mock_repo):
    install = Install(mock_repo)
    when(mock_repo).get_all_mods(...).thenReturn([])
    when(install).find_download_and_install(...)
    install.execute([])

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_set_mod_loader_by_majority(mock_repo):
    install = Install(mock_repo)
    installed_mods = [
        Mod("", "", mod_loader=ModLoaders.fabric),
        Mod("", "", mod_loader=ModLoaders.fabric),
        Mod("", "", mod_loader=ModLoaders.forge),
        Mod("", "", mod_loader=ModLoaders.unknown),
        Mod("", "", mod_loader=ModLoaders.unknown),
        Mod("", "", mod_loader=ModLoaders.unknown),
    ]

    input = ModArg("")
    expected_mod = [Mod("", "", mod_loader=ModLoaders.fabric)]
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_all_mods(...).thenReturn(installed_mods)
    when(install).find_download_and_install(expected_mod)

    install.execute([input])

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_dont_set_mod_loader(mock_repo):
    install = Install(mock_repo)
    installed_mods = []

    input = ModArg("")
    expected_mod = [Mod("", "")]
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_all_mods(...).thenReturn(installed_mods)
    when(install).find_download_and_install(expected_mod)

    install.execute([input])

    verifyStubbedInvocationsAreUsed()
    unstub()


def test_dont_set_mod_loader_when_no_majority(mock_repo):
    install = Install(mock_repo)
    installed_mods = [
        Mod("", "", mod_loader=ModLoaders.fabric),
        Mod("", "", mod_loader=ModLoaders.forge),
    ]

    input = ModArg("")
    expected_mod = [Mod("", "")]
    when(mock_repo).is_installed(...).thenReturn(False)
    when(mock_repo).get_all_mods(...).thenReturn(installed_mods)
    when(install).find_download_and_install(expected_mod)

    install.execute([input])

    verifyStubbedInvocationsAreUsed()
    unstub()
