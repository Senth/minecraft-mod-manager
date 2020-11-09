from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.remote_connection import LOGGER
from .mod_not_found_exception import ModNotFoundException
from .curse_api import CurseApi
from .dir_parser import DirParser
from .config import config
from .db import Db
from .mod import Mod, RepoTypes
from .downloader import Downloader
from . import web_driver
from .logger import Logger
from typing import List
from os import remove, path
import logging

LOGGER.setLevel(logging.WARNING)


def main():
    webdriver = web_driver.get()
    db = Db()
    try:
        # Get mods in dir and sync with DB
        dirParser = DirParser()
        installed_mods = dirParser.get_mods()
        installed_mods = db.sync_with_dir(installed_mods)

        # ACTION: Update
        if config.action == "update":
            _update(webdriver, db, installed_mods)

        elif config.action == "install":
            # TODO install
            pass

        elif config.action == "configure":
            # TODO configure
            pass

    finally:
        webdriver.close()
        db.close()


def _update(webdriver: WebDriver, db: Db, installed_mods: List[Mod]):
    # Remove mods that hasn't been supplied with args
    # But use all if no mods were supplied
    mods_to_update = installed_mods.copy()
    if len(config.mods) > 0:
        mods_to_update = list < Mod > ()
        for mod in installed_mods:
            if mod.curseforge_alias in config.mods or mod.id in config.mods:
                mods_to_update.append(mod)

    curse_parser = CurseApi(webdriver)
    downloader = Downloader()
    for mod in mods_to_update:
        latest_version = None

        try:

            # Curse
            if mod.repo_type == RepoTypes.curse:
                latest_version = curse_parser.get_latest_version(mod)

            if latest_version:
                # Only download if not same
                if mod.file != latest_version.filename:
                    downloaded_file = downloader.download(mod, latest_version)
                else:
                    downloaded_file = "skip"

                if downloaded_file:
                    # Remove old file
                    if downloaded_file != "skip":
                        Logger.info(f"Updated {mod.id} ➡ {latest_version.name}")
                        remove(path.join(config.dir, mod.file))
                        mod.file = downloaded_file

                    # Update DB
                    mod.upload_time = latest_version.upload_time
                    db.update_mod(mod)

        except ModNotFoundException as exception:
            Logger.error(str(exception))


if __name__ == "__main__":
    main()
