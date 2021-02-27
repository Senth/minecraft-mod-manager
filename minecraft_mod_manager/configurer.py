from .mod import Mod, RepoTypes
from typing import List
from .config import config
from .db import Db
from .logger import LogColors, Logger


class Configurer:
    def __init__(self, db: Db) -> None:
        self._db = db

    def configure(self, installed_mods: List[Mod]) -> None:
        for mod_arg in config.mods:
            mod_id_lower = mod_arg.id.lower()
            # Find mod
            found_mod = None
            for mod in installed_mods:
                if mod.id == mod_id_lower:
                    found_mod = mod
                    break

            if not found_mod:
                Logger.error(
                    f"Mod {mod_arg.id} not found in installed mods. Did you misspell the name?\nList installed mods by running: "
                    + f"{LogColors.command}{config.app_name} list",
                    exit=True,
                )
                return

            # Check valid repo type
            repo_type_changed = False
            if not mod_arg.repo_type.unknown:
                repo_type_changed = True

            repo_name_changed = False
            if mod_arg.name_in_repo:
                found_mod.name_in_repo = mod_arg.name_in_repo
                repo_name_changed = True

            # Updating mod
            if repo_type_changed or repo_name_changed:
                self._db.update_mod(found_mod)

                # Log info
                info = ""
                if repo_type_changed:
                    info += f"site: {found_mod.repo_type.value}"
                if repo_name_changed:
                    if len(info) > 0:
                        info += ", "
                    info += f"alias: {found_mod.name_in_repo}"

                Logger.info(f"Configured {found_mod.id}, {info}", LogColors.add)
