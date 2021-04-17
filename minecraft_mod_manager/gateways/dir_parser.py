import json
from pathlib import Path
from typing import List
from zipfile import ZipFile

from ..config import config
from ..core.entities.mod import Mod
from ..utils.logger import LogColors, Logger


class DirParser:
    @staticmethod
    def get_mods() -> List[Mod]:
        mods = []

        # Iterate through all files
        for file in Path(config.dir).glob("*.jar"):
            Logger.debug(f"Found file {file}")
            mod = DirParser.get_mod_info(file)
            mods.append(mod)

        return mods

    @staticmethod
    def get_mod_info(file: Path) -> Mod:
        with ZipFile(file, "r") as zip:
            # As a fabric mod
            with zip.open("fabric.mod.json") as json_file:
                object = json.load(json_file)
                mod = Mod(
                    id=object["id"],
                    name=object["name"],
                    version=object["version"],
                    file=file.name,
                )
                Logger.verbose(f"Found mod: {mod}", LogColors.found)
                return mod

            # LATER get mod info from filename
