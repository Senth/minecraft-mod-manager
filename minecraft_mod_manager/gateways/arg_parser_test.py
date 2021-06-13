import pytest

from ..core.entities.mod import ModArg
from ..core.entities.sites import Site, Sites
from .arg_parser import _parse_mods


@pytest.mark.parametrize(
    "name,input,expected",
    [
        (
            "Only mod ids",
            [
                "carpet",
                "litematica",
            ],
            [
                ModArg("carpet"),
                ModArg("litematica"),
            ],
        ),
        (
            "Valid repo types",
            [
                "carpet=curse",
                "litematica=modrinth",
            ],
            [
                ModArg("carpet", {Sites.curse: Site(Sites.curse)}),
                ModArg("litematica", {Sites.modrinth: Site(Sites.modrinth)}),
            ],
        ),
        (
            "Valid slugs",
            [
                "carpet=curse:fabric-carpet",
                "litematica=modrinth:litematica-fabric",
            ],
            [
                ModArg("carpet", {Sites.curse: Site(Sites.curse, slug="fabric-carpet")}),
                ModArg("litematica", {Sites.modrinth: Site(Sites.modrinth, slug="litematica-fabric")}),
            ],
        ),
        (
            "Reset site",
            ["carpet="],
            [ModArg("carpet", sites={})],
        ),
        (
            "Multiple sites for one mod",
            ["carpet=curse,modrinth"],
            [
                ModArg(
                    "carpet",
                    sites={
                        Sites.curse: Site(Sites.curse),
                        Sites.modrinth: Site(Sites.modrinth),
                    },
                )
            ],
        ),
        (
            "Multiple sites and slugs for one mod",
            ["carpet=curse:fabric-carpet,modrinth:fabric-carpet"],
            [
                ModArg(
                    "carpet",
                    sites={
                        Sites.curse: Site(Sites.curse, slug="fabric-carpet"),
                        Sites.modrinth: Site(Sites.modrinth, slug="fabric-carpet"),
                    },
                )
            ],
        ),
        (
            "Invalid repo",
            [
                "carpet=hello",
            ],
            SystemExit,
        ),
    ],
)
def test_parse_mods(name, input, expected):
    print(name)

    # Expected pass
    if type(expected) is list:
        result = _parse_mods(input)
        assert expected == result

    # Expected error
    if type(expected) is SystemExit:
        with pytest.raises(SystemExit) as e:
            _parse_mods(input)
        assert expected == e.type
