import io
from pathlib import Path

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from .jar_parser import JarParser

carpet_filename = "fabric-carpet-1.16.4-1.4.16+v201105.jar"
jei_filename = "jei-1.16.5-7.6.4.86.jar"
mod_menu_filename = "modmenu-1.14.13+build.19.jar"
capes_filename = "fabric-invalid-character.jar"


def path(filename: str) -> Path:
    return Path("fixtures").joinpath("mods").joinpath(filename)


def test_get_mod_info_when_mod_is_fabric():
    input = path(carpet_filename)
    expected = Mod(
        "carpet", "Carpet Mod in Fabric", version="1.4.16", mod_loader=ModLoaders.fabric, file=carpet_filename
    )

    result = JarParser.get_mod_info(input)

    assert expected == result


def test_get_mod_info_when_mod_is_forge():
    input = path(jei_filename)
    expected = Mod("jei", "Just Enough Items", version="7.6.4.86", mod_loader=ModLoaders.forge, file=jei_filename)

    result = JarParser.get_mod_info(input)

    assert expected == result


def test_no_mod_info_from_invalid_mod():
    input = path("invalid.jar")
    expected = None

    result = JarParser.get_mod_info(input)

    assert expected == result


def test_parse_fabric_json_with_invalid_character():
    input = path(capes_filename)
    expected = Mod("capes", "Capes", version="1.1.2", mod_loader=ModLoaders.fabric, file=capes_filename)

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
