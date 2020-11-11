from typing import List
from .mod import Mod, RepoTypes
from .dir_parser import DirParser
from .config import config
from .db import Db
from .updater import Updater
from .configurer import Configurer
from .logger import Logger, LogColors


def main():
    db = Db()
    try:
        # Get mods in dir and sync with DB
        dirParser = DirParser()
        installed_mods = dirParser.get_mods()
        installed_mods = db.sync_with_dir(installed_mods)

        # ACTION: Update
        if config.action == "update":
            updater = Updater(db)
            try:
                updater.update(installed_mods)
            finally:
                updater.close()

        elif config.action == "install":
            # TODO install
            pass

        elif config.action == "configure":
            configurer = Configurer(db)
            configurer.configure(installed_mods)

        elif config.action == "list":
            _list_mods(installed_mods)
            pass
    except:
        if db:
            db.close()


def _list_mods(installed_mods: List[Mod]):
    mod_id_max_length = 0
    mod_repo_name_max_length = 0

    for mod in installed_mods:
        if len(mod.id) > mod_id_max_length:
            mod_id_max_length = len(mod.id)
        if len(mod.repo_name_alias) > mod_repo_name_max_length:
            mod_repo_name_max_length = len(mod.repo_name_alias)

    padding = 4
    mod_id_width = mod_id_max_length + padding
    mod_repo_alias_width = mod_repo_name_max_length + padding

    message = f"{LogColors.bold}Installed mods:{LogColors.no_color}\n"
    message += f"Mod".ljust(mod_id_width) + "Alias".ljust(mod_repo_alias_width) + "Site"
    for mod in installed_mods:
        message += "\n" + f"{mod.id}".ljust(mod_id_width)
        message += f"{mod.repo_name_alias}".ljust(mod_repo_alias_width)

        if mod.repo_type != RepoTypes.unknown:
            message += f"{mod.repo_type.value}"

    Logger.info(message)


if __name__ == "__main__":
    main()
