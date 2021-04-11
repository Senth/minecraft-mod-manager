from minecraft_mod_manager.app.configure.configure_repo import ConfigureRepo
from ...core.entities.mod import Mod, ModArg, RepoTypes
from typing import List
from ...config import config
from ...utils.logger import LogColors, Logger


class Configure:
    def __init__(self, repo: ConfigureRepo) -> None:
        self._repo = repo

    def execute(self, mods: List[ModArg]) -> None:
        mods_to_update: List[Mod] = []

        for mod_arg in mods:
            mod_id_lower = mod_arg.id.lower()
            # Find mod
            found_mod = self._repo.find_mod(mod_id_lower)

            if not found_mod:
                Logger.error(
                    f"Mod {mod_arg.id} not found in installed mods. Did you misspell the name?\nList installed mods by running: "
                    + f"{LogColors.command}{config.app_name} list",
                    exit=True,
                )
                return

            if mod_arg.repo_type != RepoTypes.unknown:
                found_mod.repo_type = mod_arg.repo_type

            if mod_arg.alias:
                found_mod.alias = mod_arg.alias

            # Updating mod
            mods_to_update.append(found_mod)

        for mod in mods_to_update:
            self._repo.update_mod(mod)

            # Log info
            info = ""
            if mod.repo_type != RepoTypes.unknown:
                info += f"site: {mod.repo_type.value}"
            if len(mod.alias):
                if len(info) > 0:
                    info += ", "
                info += f"alias: {mod.alias}"

            Logger.info(f"Configured {mod.id}; {info}", LogColors.add)
