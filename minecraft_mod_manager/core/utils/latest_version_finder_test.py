from typing import List, Union

import pytest

from ...config import config
from ..entities.mod import Mod
from ..entities.mod_loaders import ModLoaders
from ..entities.sites import Sites
from ..entities.version_info import Stabilities, VersionInfo
from .latest_version_finder import LatestVersionFinder


class Filter:
    def __init__(
        self, version: Union[str, None] = None, loader=ModLoaders.unknown, stability=Stabilities.unknown
    ) -> None:
        self.version = version
        self.loader = loader
        self.stability = stability


class Test:
    def __init__(
        self, name: str, mod: Mod, versions: List[VersionInfo], expected: Union[VersionInfo, None], filter=Filter()
    ) -> None:
        self.name = name
        self.mod = mod
        self.versions = versions
        self.filter = filter
        self.expected = expected


def mod(loader=ModLoaders.unknown):
    return Mod("", "", mod_loader=loader)


def version_info(
    stability=Stabilities.release, mod_loaders: List[ModLoaders] = [], versions: List[str] = [], uploaded=0
) -> VersionInfo:
    return VersionInfo(
        stability=stability,
        mod_loaders=set(mod_loaders),
        site=Sites.curse,
        minecraft_versions=versions,
        upload_time=uploaded,
        download_url="",
    )


def set_filter(filter: Filter) -> None:
    config.filter.loader = filter.loader
    config.filter.stability = filter.stability
    config.filter.version = filter.version


def reset_filter() -> None:
    config.filter.loader = ModLoaders.unknown
    config.filter.stability = Stabilities.unknown
    config.filter.version = None


@pytest.mark.parametrize(
    "test",
    [
        (
            Test(
                name="Find itself when only one version is specified",
                mod=mod(),
                versions=[
                    version_info(),
                ],
                expected=version_info(),
            )
        ),
        (
            Test(
                name="Find latest version without filters",
                mod=mod(),
                versions=[
                    version_info(uploaded=10),
                    version_info(uploaded=20, stability=Stabilities.beta),
                    version_info(uploaded=50, stability=Stabilities.alpha),
                    version_info(uploaded=30, versions=["1.16.5"]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                expected=version_info(uploaded=50, stability=Stabilities.alpha),
            )
        ),
        (
            Test(
                name="Find latest version excluding alpha",
                mod=mod(),
                versions=[
                    version_info(uploaded=10),
                    version_info(uploaded=20, stability=Stabilities.beta),
                    version_info(uploaded=50, stability=Stabilities.alpha),
                    version_info(uploaded=30, versions=["1.16.5"]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(stability=Stabilities.beta),
                expected=version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
            )
        ),
        (
            Test(
                name="Find latest beta version excluding alpha",
                mod=mod(),
                versions=[
                    version_info(uploaded=10),
                    version_info(uploaded=45, stability=Stabilities.beta),
                    version_info(uploaded=50, stability=Stabilities.alpha),
                    version_info(uploaded=30, versions=["1.16.5"]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(stability=Stabilities.beta),
                expected=version_info(uploaded=45, stability=Stabilities.beta),
            )
        ),
        (
            Test(
                name="Find latest version using MC version",
                mod=mod(),
                versions=[
                    version_info(uploaded=10, versions=["1.16.5"]),
                    version_info(uploaded=20, versions=["1.17", "Fabric", "1.16.5"]),
                    version_info(uploaded=50, stability=Stabilities.alpha),
                    version_info(uploaded=30, versions=["toast", "1.16.5"]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(version="1.16.5"),
                expected=version_info(uploaded=30, versions=["toast", "1.16.5"]),
            )
        ),
        (
            Test(
                name="Find latest version by mod loader",
                mod=mod(),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(loader=ModLoaders.forge),
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
            )
        ),
        (
            Test(
                name="Find latest version by mod loader",
                mod=mod(),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(loader=ModLoaders.fabric),
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mob loader in mod",
                mod=mod(loader=ModLoaders.forge),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader in mod",
                mod=mod(loader=ModLoaders.fabric),
                versions=[
                    version_info(uploaded=40, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.forge, ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
                ],
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader in mod when loader is specified in version_info",
                mod=mod(loader=ModLoaders.fabric),
                versions=[
                    version_info(uploaded=50, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.forge, ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=40),
                ],
                expected=version_info(uploaded=40),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader using many mods in mod",
                mod=mod(loader=ModLoaders.fabric),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.forge, ModLoaders.fabric]),
                ],
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.forge, ModLoaders.fabric]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader overriding mod",
                mod=mod(loader=ModLoaders.fabric),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(loader=ModLoaders.forge),
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.forge]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader overriding mod",
                mod=mod(loader=ModLoaders.forge),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
                ],
                filter=Filter(loader=ModLoaders.fabric),
                expected=version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
            )
        ),
        (
            Test(
                name="Find latest version filter by mod loader override mod when loader is specified in version_info",
                mod=mod(),
                versions=[
                    version_info(uploaded=50, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.forge, ModLoaders.fabric]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric]),
                    version_info(uploaded=40),
                ],
                filter=Filter(loader=ModLoaders.fabric),
                expected=version_info(uploaded=40),
            )
        ),
        (
            Test(
                name="Find latest version by applying all filters",
                mod=mod(),
                versions=[
                    version_info(
                        uploaded=99,
                        mod_loaders=[ModLoaders.forge],
                        stability=Stabilities.release,
                        versions=["1.16.5"],
                    ),
                    version_info(
                        uploaded=99,
                        mod_loaders=[ModLoaders.fabric],
                        stability=Stabilities.alpha,
                        versions=["1.16.5"],
                    ),
                    version_info(
                        uploaded=99,
                        mod_loaders=[ModLoaders.fabric],
                        stability=Stabilities.release,
                        versions=["1.16.4", "1.16.6"],
                    ),
                    version_info(
                        uploaded=10,
                        mod_loaders=[ModLoaders.fabric],
                        stability=Stabilities.release,
                        versions=["1.17", "1.16.5"],
                    ),
                    version_info(
                        uploaded=20,
                        mod_loaders=[ModLoaders.fabric],
                        stability=Stabilities.release,
                        versions=["1.16.5"],
                    ),
                    version_info(
                        uploaded=30,
                        mod_loaders=[ModLoaders.fabric],
                        stability=Stabilities.beta,
                        versions=["1.16.5"],
                    ),
                ],
                filter=Filter(loader=ModLoaders.fabric, version="1.16.5", stability=Stabilities.beta),
                expected=version_info(
                    uploaded=30,
                    mod_loaders=[ModLoaders.fabric],
                    stability=Stabilities.beta,
                    versions=["1.16.5"],
                ),
            )
        ),
        (
            Test(
                name="Find no mod found using filters",
                mod=mod(),
                versions=[
                    version_info(uploaded=10, mod_loaders=[ModLoaders.forge], versions=["1.16.4"]),
                    version_info(uploaded=20, mod_loaders=[ModLoaders.fabric], versions=["1.16.5"]),
                    version_info(uploaded=40, mod_loaders=[ModLoaders.forge]),
                    version_info(uploaded=30, mod_loaders=[ModLoaders.fabric], versions=["1.16.2", "1.16.5"]),
                ],
                filter=Filter(loader=ModLoaders.forge, version="1.16.5"),
                expected=None,
            )
        ),
    ],
)
def test_find_latest_version(test: Test):
    print(test.name)
    set_filter(test.filter)
    result = LatestVersionFinder.find_latest_version(test.mod, test.versions, filter=True)
    reset_filter()
    assert test.expected == result


def test_find_latest_version_unfiltered():
    set_filter(Filter(loader=ModLoaders.forge, version="1.16.5"))
    versions = [
        version_info(uploaded=10, mod_loaders=[ModLoaders.forge], versions=["1.16.4"]),
        version_info(uploaded=20, mod_loaders=[ModLoaders.fabric], versions=["1.16.5"]),
        version_info(uploaded=40, mod_loaders=[ModLoaders.fabric]),
        version_info(uploaded=30, mod_loaders=[ModLoaders.fabric], versions=["1.16.2", "1.16.5"]),
    ]
    expected = version_info(uploaded=40, mod_loaders=[ModLoaders.fabric])
    result = LatestVersionFinder.find_latest_version(mod(), versions, filter=False)
    reset_filter()
    assert expected == result
