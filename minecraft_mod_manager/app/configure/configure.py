from typing import List, Sequence

from ...config import config
from ...core.entities.mod import Mod, ModArg, Sites
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
                Logger.error(
                    f"Mod {mod_arg.id} not found in installed mods. "
                    + "Did you misspell the name?\nList installed mods by running: "
                    + f"{LogColors.command}{config.app_name} list",
                    exit=True,
                )
                return

            if mod_arg.site != Sites.unknown:
                found_mod.site = mod_arg.site

            if mod_arg.site_slug:
                found_mod.site_slug = mod_arg.site_slug

            # Updating mod
            mods_to_update.append(found_mod)

        for mod in mods_to_update:
            self._repo.update_mod(mod)

            # Log info
            info = ""
            if mod.site != Sites.unknown:
                info += f"site: {mod.site.value}"
            if mod.site_slug:
                if len(info) > 0:
                    info += ", "
                info += f"alias: {mod.site_slug}"

            Logger.info(f"Configured {mod.id}; {info}", LogColors.add)
