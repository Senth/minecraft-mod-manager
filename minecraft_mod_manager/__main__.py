from typing import List

from .config import config
from .configurer import Configure
from .db import Db
from .dir_parser import DirParser
from .installer import Installer
from .logger import LogColors, Logger
from .mod import Mod, RepoTypes
from .updater import Updater


def main():
    db = Db()
    try:
        # Get mods in dir and sync with DB
        installed_mods = DirParser.get_mods()
        installed_mods = db.sync_with_dir(installed_mods)

        # ACTION: Update
        if config.action == "update":
            updater = Updater(db)
            try:
                updater.update(installed_mods)
            finally:
                updater.close()

        elif config.action == "install":
            installer = Installer(db, installed_mods)
            try:
                installer.install(config.mods)
            finally:
                installer.close()

        elif config.action == "configure":
            configurer = Configure(db)
            configurer.execute(installed_mods)

        elif config.action == "list":
            _list_mods(installed_mods)
            pass
    finally:
        if db:
            db.close()


if __name__ == "__main__":
    main()
