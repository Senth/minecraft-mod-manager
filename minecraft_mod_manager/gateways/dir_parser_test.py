from pathlib import Path

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from .dir_parser import DirParser

carpet_filename = "fabric-carpet-1.16.4-1.4.16+v201105.jar"
jei_filename = "jei-1.16.5-7.6.4.86.jar"
mod_menu_filename = "modmenu-1.14.13+build.19.jar"


def test_get_mod_info_when_mod_is_fabric():
    filename = carpet_filename
    input = Path(f"fixtures/{filename}")
    expected = Mod("carpet", "Carpet Mod in Fabric", version="1.4.16", mod_loader=ModLoaders.fabric, file=filename)

    result = DirParser.get_mod_info(input)

    assert expected == result


def test_get_mod_info_when_mod_is_forge():
    filename = jei_filename
    input = Path(f"fixtures/{filename}")
    expected = Mod("jei", "Just Enough Items", version="7.6.4.86", mod_loader=ModLoaders.forge, file=filename)

    result = DirParser.get_mod_info(input)

    assert expected == result


def test_no_mod_info_from_invalid_mod():
    filename = "invalid.jar"
    input = Path(f"fixtures/{filename}")
    expected = None

    result = DirParser.get_mod_info(input)

    assert expected == result


def test_get_mods():
    input = Path("fixtures")
    expected = [
        Mod("carpet", "Carpet Mod in Fabric", version="1.4.16", mod_loader=ModLoaders.fabric, file=carpet_filename),
        Mod("jei", "Just Enough Items", version="7.6.4.86", mod_loader=ModLoaders.forge, file=jei_filename),
        Mod("modmenu", "Mod Menu", version="1.14.13+build.19", mod_loader=ModLoaders.fabric, file=mod_menu_filename),
    ]

    result = DirParser.get_mods(input)

    assert expected == result
