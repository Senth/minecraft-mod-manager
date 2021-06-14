from typing import Dict, List, Sequence

from ...config import config
from ...core.entities.mod import Mod, ModArg
from ...core.entities.sites import Site, Sites
from ...utils.logger import LogColors, Logger
from ..configure.configure_repo import ConfigureRepo


class Configure:
    def __init__(self, repo: ConfigureRepo) -> None:
        self._repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods_to_update: List[Mod] = []

        for mod_arg in mods:
            mod_id_lower = mod_arg.id.lower()
            # Find mod
            found_mod = self._repo.get_mod(mod_id_lower)

            if not found_mod:
                Logger.info(
                    f"Mod {mod_arg.id} not found in installed mods. "
                    + "Did you misspell the name?\nList installed mods by running: "
                    + f"{LogColors.command}{config.app_name} list",
                    LogColors.error,
                    exit=True,
                )
                return

            if isinstance(mod_arg.sites, dict):
                Configure._update_sites(found_mod, mod_arg.sites)

            # Updating mod
            mods_to_update.append(found_mod)

        for mod in mods_to_update:
            self._repo.update_mod(mod)

            # Sites info
            site_info = ""
            for site in mod.sites.values():
                if len(site_info) > 0:
                    site_info += ", "
                site_info += site.get_configure_string()

            Logger.info(f"Configured sites for {mod.id}; {{{site_info}}}", LogColors.add)

    @staticmethod
    def _update_sites(mod: Mod, sites: Dict[Sites, Site]) -> None:
        old_sites = mod.sites
        mod.sites = sites

        if old_sites:
            for old_site in old_sites.values():
                if old_site.id:
                    if mod.sites and old_site.name in mod.sites:
                        mod.sites[old_site.name].id = old_site.id
