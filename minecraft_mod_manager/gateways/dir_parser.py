import json
from pathlib import Path
from typing import List, Union
from zipfile import ZipFile

import toml

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..utils.logger import LogColors, Logger


class DirParser:
    _fabric_file = "fabric.mod.json"
    _forge_file = "META-INF/mods.toml"

    @staticmethod
    def get_mods(dir: Path) -> List[Mod]:
        mods = []

        # Iterate through all files
        for file in dir.glob("*.jar"):
            Logger.debug(f"Found file {file}")
            mod = DirParser.get_mod_info(file)
            if mod:
                DirParser._log_found_mod(mod)
                mods.append(mod)

        return mods

    @staticmethod
    def get_mod_info(file: Path) -> Union[Mod, None]:
        mod: Union[Mod, None] = None
        with ZipFile(file, "r") as zip:
            if DirParser._is_fabric(zip):
                mod = DirParser._parse_fabric(zip)
            elif DirParser._is_forge(zip):
                mod = DirParser._parse_forge(zip)

        if mod:
            mod.file = file.name

        return mod

    @staticmethod
    def _is_fabric(zip: ZipFile) -> bool:
        return DirParser._fabric_file in zip.namelist()

    @staticmethod
    def _parse_fabric(zip: ZipFile) -> Mod:
        with zip.open(DirParser._fabric_file) as json_file:
            object = json.load(json_file)
            return Mod(
                id=object["id"],
                name=object["name"],
                version=object["version"],
                mod_loader=ModLoaders.fabric,
            )

    @staticmethod
    def _is_forge(zip: ZipFile) -> bool:
        return DirParser._forge_file in zip.namelist()

    @staticmethod
    def _parse_forge(zip: ZipFile) -> Mod:
        with zip.open(DirParser._forge_file) as file:
            lines = file.readlines()
            full_doc = ""
            for line in lines:
                full_doc += f"{line.decode('utf-8')}\n"
            obj = toml.loads(full_doc)
            mods = obj["mods"][0]
            return Mod(
                mods["modId"],
                mods["displayName"],
                mod_loader=ModLoaders.forge,
                version=mods["version"],
            )

    @staticmethod
    def _log_found_mod(mod: Mod) -> None:
        Logger.verbose(f"Found {mod.mod_loader} mod: {mod}", LogColors.found)
