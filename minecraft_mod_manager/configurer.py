from .mod import Mod, RepoTypes
from typing import List
from .config import config
from .db import Db
from .logger import LogColors, Logger


class Configurer:
    def __init__(self, db: Db) -> None:
        self._db = db

    def configure(self, installed_mods: List[Mod]) -> None:
        for repo_type, mod_id, repo_name_alias in config.mods:
            mod_id_lower = mod_id.lower()
            # Find mod
            found_mod = None
            for mod in installed_mods:
                if mod.id == mod_id_lower:
                    found_mod = mod
                    break

            if not found_mod:
                Logger.error(
                    f"Mod {mod_id} not found in installed mods. Did you misspell the name?\nList installed mods by running:\n"
                    + f"{LogColors.command}{config.app_name} list",
                    exit=True,
                )
                return

            # Check valid repo type
            repo_type_changed = False
            if repo_type:
                try:
                    found_mod.repo_type = RepoTypes[repo_type.lower()]
                    repo_type_changed = True
                except KeyError:
                    valid_types = ""
                    for valid_repo in RepoTypes:
                        valid_types += f"\n  {valid_repo.value}"

                    Logger.error(
                        f"'{repo_type}' isn't a valid site name. Valid names include:{valid_types}",
                        exit=True,
                    )

            repo_name_changed = False
            if repo_name_alias:
                found_mod.repo_name_alias = repo_name_alias
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
                    info += f"alias: {found_mod.repo_name_alias}"

                Logger.info(f"Configured {found_mod.id}, {info}", LogColors.add)
