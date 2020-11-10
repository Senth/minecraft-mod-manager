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
from .logger import LogColors, Logger
from typing import List
from os import remove, path
import logging


def main():
    webdriver = web_driver.get()
    LOGGER.setLevel(logging.WARNING)
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
        mods_to_update: List[Mod] = []
        for mod in installed_mods:
            if mod.repo_name_alias in config.mods or mod.id in config.mods:
                mods_to_update.append(mod)

    curse_parser = CurseApi(webdriver)
    downloader = Downloader()
    for mod in mods_to_update:
        latest_version = None
        was_unknown = mod.repo_type == RepoTypes.unknown

        # Curse
        try:
            if mod.repo_type == RepoTypes.curse or mod.repo_type == RepoTypes.unknown:
                latest_version = curse_parser.get_latest_version(mod)
        except ModNotFoundException as exception:
            Logger.error(str(exception), exit=True)

        # Update DB mod if a repo was found with a matching mod name
        if was_unknown and mod.repo_type != RepoTypes.unknown:
            db.update_mod(mod)

        if latest_version:
            # Only download if not same
            if mod.file != latest_version.filename:
                downloaded_file = downloader.download(mod, latest_version)
            else:
                downloaded_file = "skip"

            if downloaded_file:
                # Remove old file
                if downloaded_file != "skip":
                    Logger.info(
                        f"Updated {mod.repo_name_alias} ➡  {latest_version.name}",
                        LogColors.green,
                    )
                    remove(path.join(config.dir, mod.file))
                    mod.file = downloaded_file

                # Update DB
                mod.upload_time = latest_version.upload_time
                db.update_mod(mod)


if __name__ == "__main__":
    main()
