from typing import List, Union

from ...config import config
from ..entities.mod import Mod
from ..entities.mod_loaders import ModLoaders
from ..entities.version_info import Stabilities, VersionInfo


class LatestVersionFinder:
    @staticmethod
    def find_latest_version(mod: Mod, versions: List[VersionInfo]) -> Union[VersionInfo, None]:
        latest_version: Union[VersionInfo, None] = None

        for version in versions:
            if not LatestVersionFinder._is_filtered(mod, version):
                if not latest_version or version.upload_time > latest_version.upload_time:
                    latest_version = version

        return latest_version

    @staticmethod
    def _is_filtered(mod: Mod, version: VersionInfo) -> bool:
        if LatestVersionFinder._is_filtered_by_stability(version):
            return True
        if LatestVersionFinder._is_filtered_by_mc_version(version):
            return True
        if LatestVersionFinder._is_filtered_by_mod_loader(mod.mod_loader, version):
            return True
        return False

    @staticmethod
    def _is_filtered_by_stability(version: VersionInfo) -> bool:
        if config.filter.stability == Stabilities.alpha:
            return False
        elif config.filter.stability == Stabilities.beta:
            return version.stability == Stabilities.alpha
        elif config.filter.stability == Stabilities.release:
            return version.stability == Stabilities.beta or version.stability == Stabilities.alpha
        return False

    @staticmethod
    def _is_filtered_by_mc_version(version: VersionInfo) -> bool:
        if config.filter.version:
            return config.filter.version not in version.minecraft_versions
        return False

    @staticmethod
    def _is_filtered_by_mod_loader(prev: ModLoaders, version: VersionInfo) -> bool:
        if config.filter.loader == ModLoaders.unknown:
            if prev != ModLoaders.unknown:
                return prev not in version.mod_loaders
            return False
        return config.filter.loader not in version.mod_loaders
