import json
from pathlib import Path
from typing import List, Union
from zipfile import ZipFile

import toml

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..utils.logger import LogColors, Logger


class JarParser:
    _fabric_file = "fabric.mod.json"
    _forge_file = "META-INF/mods.toml"

    def __init__(self, dir: Path) -> None:
        self._mods: List[Mod] = []
        self._dir = dir

    @property
    def mods(self) -> List[Mod]:
        # Return cached value
        if len(self._mods) > 0:
            return self._mods

        # Iterate through all files
        for file in self._dir.glob("*.jar"):
            Logger.debug(f"Found file {file}")
            mod = JarParser.get_mod_info(file)
            if mod:
                JarParser._log_found_mod(mod)
                self._mods.append(mod)

        return self._mods

    @staticmethod
    def get_mod_info(file: Path) -> Union[Mod, None]:
        mod: Union[Mod, None] = None

        try:
            with ZipFile(file, "r") as zip:
                if JarParser._is_fabric(zip):
                    mod = JarParser._parse_fabric(zip)
                elif JarParser._is_forge(zip):
                    mod = JarParser._parse_forge(zip)
                else:
                    Logger.info(f"No mod info found for {file.name}", LogColors.warning)
        except Exception:
            Logger.error(f"Failed to parse mod file {file}", print_exception=True)

        if mod:
            mod.file = file.name
            return mod

        return None

    @staticmethod
    def _is_fabric(zip: ZipFile) -> bool:
        return JarParser._fabric_file in zip.namelist()

    @staticmethod
    def _parse_fabric(zip: ZipFile) -> Mod:
        with zip.open(JarParser._fabric_file) as json_file:
            full_doc = json_file.read().decode("utf-8", "ignore")
            object = json.loads(full_doc, strict=False)
            return Mod(
                id=object["id"],
                name=object["name"],
                version=object["version"],
                mod_loader=ModLoaders.fabric,
            )

    @staticmethod
    def _is_forge(zip: ZipFile) -> bool:
        return JarParser._forge_file in zip.namelist()

    @staticmethod
    def _parse_forge(zip: ZipFile) -> Mod:
        with zip.open(JarParser._forge_file) as file:
            full_doc = file.read().decode("utf-8", "ignore")
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
        Logger.verbose(f"Found {mod.mod_loader.value} mod: {mod}", LogColors.found)
