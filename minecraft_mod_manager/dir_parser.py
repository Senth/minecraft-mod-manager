from pathlib import Path
from zipfile import ZipFile
from .config import config
from .logger import LogColors, Logger
from .mod import Mod
from typing import List
import json


class DirParser:
    def get_mods(self) -> List[Mod]:
        mods = []

        # Iterate through all files
        for file in Path(config.dir).glob("*.jar"):
            Logger.debug(f"Found file {file}")
            mod = self._get_mod_info(file)
            mods.append(mod)

        return mods

    def _get_mod_info(self, file: Path) -> Mod:
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