from pathlib import Path

import pytest

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from .jar_parser import JarParser

testdata_dir = Path(__file__).parent.joinpath("testdata")
mod_dir = testdata_dir.joinpath("mods")

forge_valid = Mod(
    "jei",
    "Just Enough Items",
    version="7.6.4.86",
    mod_loader=ModLoaders.forge,
    file="forge-valid.jar",
)
fabric_valid = Mod(
    "carpet",
    "Carpet Mod in Fabric",
    version="1.4.16",
    mod_loader=ModLoaders.fabric,
    file="fabric-valid.jar",
)
fabric_invalid_character = Mod(
    "capes",
    "Capes",
    version="1.1.2",
    mod_loader=ModLoaders.fabric,
    file="fabric-invalid-character.jar",
)
fabric_invalid_control_character = Mod(
    "itemmodelfix",
    "Item Model Fix",
    version="1.0.2+1.17",
    mod_loader=ModLoaders.fabric,
    file="fabric-invalid-control-character.jar",
)
toml_inline_comment = Mod(
    "twilightforest",
    "The Twilight Forest",
    version="${file.jarVersion}",
    mod_loader=ModLoaders.forge,
    file="toml-inline-comment.jar",
)


def path(filename: str) -> Path:
    return mod_dir.joinpath(filename)


@pytest.mark.parametrize(
    "name,file,expected",
    [
        (
            "Returns mod info when fabric",
            fabric_valid.file,
            fabric_valid,
        ),
        (
            "Returns mod info when forge",
            forge_valid.file,
            forge_valid,
        ),
        (
            "Returns no mod info when invalid mod",
            "invalid.jar",
            None,
        ),
        (
            "Handles invalid characters in fabric json file",
            fabric_invalid_character.file,
            fabric_invalid_character,
        ),
        (
            "Handles invalid control character in fabric json file",
            fabric_invalid_control_character.file,
            fabric_invalid_control_character,
        ),
        (
            "Handle missing key 'mods' in forge file",
            toml_inline_comment.file,
            toml_inline_comment,
        ),
    ],
)
def test_get_mod_info(name, file, expected):
    print(name)
    input = path(file)

    result = JarParser._get_mod_info(input)

    assert expected == result


def test_get_mods():
    expected = [
        forge_valid,
        fabric_valid,
        fabric_invalid_character,
        fabric_invalid_control_character,
        toml_inline_comment,
    ]
    jar_parser = JarParser(mod_dir)
    result = jar_parser.mods

    assert sorted(expected) == sorted(result)


def test_unbalanced_quotes():
    with open(testdata_dir.joinpath("unbalanced-quotes.toml")) as file:
        obj = JarParser._load_toml(file.read())

        assert obj["basic_wrong"] == "This description spans over multiple lines. But doesn't use correct syntax"
        assert obj["literal_wrong"] == "Multiline comment with more lines "
        assert obj["basic_correct"] == "this is a correct\ncomment\n"
        assert obj["literal_correct"] == "this is a correct\ncomment\n"
