from pathlib import Path

import pytest

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from .jar_parser import JarParser

jei = Mod(
    "jei",
    "Just Enough Items",
    version="7.6.4.86",
    mod_loader=ModLoaders.forge,
    file="jei-1.16.5-7.6.4.86.jar",
)
carpet = Mod(
    "carpet",
    "Carpet Mod in Fabric",
    version="1.4.16",
    mod_loader=ModLoaders.fabric,
    file="fabric-carpet-1.16.4-1.4.16+v201105.jar",
)
mod_menu = Mod(
    "modmenu",
    "Mod Menu",
    version="1.14.13+build.19",
    mod_loader=ModLoaders.fabric,
    file="modmenu-1.14.13+build.19.jar",
)
capes = Mod(
    "capes",
    "Capes",
    version="1.1.2",
    mod_loader=ModLoaders.fabric,
    file="fabric-invalid-character.jar",
)
item_model_fix = Mod(
    "itemmodelfix",
    "Item Model Fix",
    version="1.0.2+1.17",
    mod_loader=ModLoaders.fabric,
    file="fabric-invalid-control-character.jar",
)


def path(filename: str) -> Path:
    return Path("fixtures").joinpath("mods").joinpath(filename)


@pytest.mark.parametrize(
    "name,file,expected",
    [
        (
            "Returns mod info when fabric",
            carpet.file,
            carpet,
        ),
        (
            "Returns mod info when forge",
            jei.file,
            jei,
        ),
        (
            "Returns no mod info when invalid mod",
            "invalid.jar",
            None,
        ),
        (
            "Returns valid mod info when contains invalid characters",
            capes.file,
            capes,
        ),
        (
            "Returns valid mod info when it has an invalid control character",
            item_model_fix.file,
            item_model_fix,
        ),
    ],
)
def test_get_mod_info(name, file, expected):
    print(name)
    input = path(file)

    result = JarParser.get_mod_info(input)

    assert expected == result


def test_get_mods():
    input = Path("fixtures").joinpath("mods")
    expected = [jei, carpet, mod_menu, capes, item_model_fix]
    jar_parser = JarParser(input)
    result = jar_parser.mods

    assert sorted(expected) == sorted(result)
