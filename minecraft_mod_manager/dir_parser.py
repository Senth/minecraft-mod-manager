from pathlib import Path
from zipfile import ZipFile
from .config import config
from .logger import Logger
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
            with zip.open("fabric.mod.json") as json_file:
                object = json.load(json_file)
                mod = Mod(object["id"], object["name"], object["version"], file.name)
                Logger.info(f"Found mod: {mod}")
                return mod
