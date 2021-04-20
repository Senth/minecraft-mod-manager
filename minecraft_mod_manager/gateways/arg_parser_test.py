import pytest

from ..core.entities.mod import ModArg
from ..core.entities.sites import Sites
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
                ModArg(Sites.unknown, "carpet", "carpet"),
                ModArg(Sites.unknown, "litematica", "litematica"),
            ],
        ),
        (
            "Valid repo types",
            [
                "curse:carpet",
                "curse:litematica",
            ],
            [
                ModArg(Sites.curse, "carpet", "carpet"),
                ModArg(Sites.curse, "litematica", "litematica"),
            ],
        ),
        (
            "Valid aliases",
            [
                "carpet=fabric-carpet",
                "litematica=litematica-fabric",
            ],
            [
                ModArg(Sites.unknown, "carpet", "fabric-carpet"),
                ModArg(Sites.unknown, "litematica", "litematica-fabric"),
            ],
        ),
        (
            "Valid repo and alias",
            [
                "curse:carpet=fabric-carpet",
                "curse:litematica=litematica-fabric",
            ],
            [
                ModArg(Sites.curse, "carpet", "fabric-carpet"),
                ModArg(Sites.curse, "litematica", "litematica-fabric"),
            ],
        ),
        (
            "Invalid repo",
            [
                "hello:carpet",
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
