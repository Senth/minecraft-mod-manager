from typing import List, Union

from ...config import config
from ..entities.mod import Mod
from ..entities.mod_loaders import ModLoaders
from ..entities.version_info import Stabilities, VersionInfo


class LatestVersionFinder:
    @staticmethod
    def find_latest_version(mod: Mod, versions: List[VersionInfo], filter: bool) -> Union[VersionInfo, None]:
        latest_version: Union[VersionInfo, None] = None

        for version in versions:
            if not filter or not LatestVersionFinder.is_filtered(mod, version):
                if not latest_version or version.upload_time > latest_version.upload_time:
                    latest_version = version

        return latest_version

    @staticmethod
    def is_filtered(mod: Mod, version: VersionInfo) -> bool:
        if LatestVersionFinder.is_filtered_by_stability(version):
            return True
        if LatestVersionFinder.is_filtered_by_mc_version(version):
            return True
        if LatestVersionFinder.is_filtered_by_mod_loader(mod.mod_loader, version):
            return True
        return False

    @staticmethod
    def is_filtered_by_stability(version: VersionInfo) -> bool:
        if config.filter.stability == Stabilities.alpha:
            return False
        elif config.filter.stability == Stabilities.beta:
            return version.stability == Stabilities.alpha
        elif config.filter.stability == Stabilities.release:
            return version.stability == Stabilities.beta or version.stability == Stabilities.alpha
        return False

    @staticmethod
    def is_filtered_by_mc_version(version: VersionInfo) -> bool:
        if config.filter.version:
            return config.filter.version not in version.minecraft_versions
        return False

    @staticmethod
    def is_filtered_by_mod_loader(prev: ModLoaders, version: VersionInfo) -> bool:
        """Check whether this version should be filtered by mod_loader.
        Will check both if a global filter has been set, otherwise it will match against
        the already install version's mod loader (if one exists).

        Args:
            prev (ModLoaders): The mod loader of the existing installed version
            version (VersionInfo): Downloaded version to filter

        Returns:
            bool: True -> filter/remove; false -> keep it
        """
        # No mod loaders specified in version, match all
        if len(version.mod_loaders) == 0:
            return False

        # Use global filter
        elif config.filter.loader != ModLoaders.unknown:
            return config.filter.loader not in version.mod_loaders

        # Use filter from previous version
        else:
            if prev != ModLoaders.unknown:
                return prev not in version.mod_loaders

        return False
