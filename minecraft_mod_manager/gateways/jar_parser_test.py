from pathlib import Path

import pytest

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from .jar_parser import JarParser

carpet_filename = "fabric-carpet-1.16.4-1.4.16+v201105.jar"
jei_filename = "jei-1.16.5-7.6.4.86.jar"
mod_menu_filename = "modmenu-1.14.13+build.19.jar"
capes_filename = "fabric-invalid-character.jar"


def path(filename: str) -> Path:
    return Path("fixtures").joinpath("mods").joinpath(filename)


@pytest.mark.parametrize(
    "name,file,expected",
    [
        (
            "Returns mod info when fabric",
            carpet_filename,
            Mod(
                "carpet",
                "Carpet Mod in Fabric",
                version="1.4.16",
                mod_loader=ModLoaders.fabric,
                file=carpet_filename,
            ),
        ),
        (
            "Returns mod info when forge",
            jei_filename,
            Mod(
                "jei",
                "Just Enough Items",
                version="7.6.4.86",
                mod_loader=ModLoaders.forge,
                file=jei_filename,
            ),
        ),
        (
            "Returns no mod info when invalid mod",
            "invalid.jar",
            None,
        ),
        (
            "Returns valid mod info when contains invalid characters",
            capes_filename,
            Mod(
                "capes",
                "Capes",
                version="1.1.2",
                mod_loader=ModLoaders.fabric,
                file=capes_filename,
            ),
        ),
    ],
)
def test_get_mod_info(name, file, expected):
    input = path(file)

    result = JarParser.get_mod_info(input)

    assert expected == result


def test_get_mods():
    input = Path("fixtures").joinpath("mods")
    expected = [
        Mod("jei", "Just Enough Items", version="7.6.4.86", mod_loader=ModLoaders.forge, file=jei_filename),
        Mod("carpet", "Carpet Mod in Fabric", version="1.4.16", mod_loader=ModLoaders.fabric, file=carpet_filename),
        Mod("modmenu", "Mod Menu", version="1.14.13+build.19", mod_loader=ModLoaders.fabric, file=mod_menu_filename),
        Mod("capes", "Capes", version="1.1.2", mod_loader=ModLoaders.fabric, file=capes_filename),
    ]
    jar_parser = JarParser(input)
    result = jar_parser.mods

    assert sorted(expected) == sorted(result)
