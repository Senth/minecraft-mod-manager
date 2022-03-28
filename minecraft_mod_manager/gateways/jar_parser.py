import json
import re
from pathlib import Path
from typing import Any, List, MutableMapping, Union
from zipfile import ZipFile

import toml
from tealprint import TealPrint

from ..core.entities.mod import Mod
from ..core.entities.mod_loaders import ModLoaders
from ..core.errors.mod_file_invalid import ModFileInvalid
from ..utils.log_colors import LogColors


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
            TealPrint.debug(f"Found file {file}")
            try:
                mod = JarParser._get_mod_info(file)
                if mod:
                    JarParser._log_found_mod(mod)
                    self._mods.append(mod)
            except ModFileInvalid as e:
                TealPrint.warning(str(e))

        return self._mods

    def get_mod(self, file: str) -> Union[Mod, None]:
        return JarParser._get_mod_info(self._dir.joinpath(file))

    @staticmethod
    def _get_mod_info(file: Path) -> Union[Mod, None]:
        mod: Union[Mod, None] = None

        try:
            with ZipFile(file, "r") as zip:
                if JarParser._is_fabric(zip):
                    mod = JarParser._parse_fabric(zip)
                elif JarParser._is_forge(zip):
                    mod = JarParser._parse_forge(zip)
                else:
                    TealPrint.warning(f"No mod info found for {file.name}")
        except Exception:
            TealPrint.error(f"Failed to parse mod file {file}", print_exception=True, print_report_this=True)
            raise ModFileInvalid(file)

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
            obj = JarParser._load_toml(full_doc)
            mods = obj["mods"][0]
            return Mod(
                mods["modId"],
                mods["displayName"],
                mod_loader=ModLoaders.forge,
                version=mods["version"],
            )

    @staticmethod
    def _load_toml(toml_str: str) -> MutableMapping[str, Any]:
        try:
            return toml.loads(toml_str)
        except toml.TomlDecodeError:
            return toml.loads(JarParser._fix_toml_multiline_string(toml_str))

    @staticmethod
    def _fix_toml_multiline_string(toml_str: str) -> str:
        # TODO fix this as it makes everything on one line
        new = ""
        basic_start = re.compile(r"=\s*\"[^\"]")
        basic_end = re.compile(r"\"\s*$|\"[\s#]+")
        literal_start = re.compile(r"=\s*'[^']")
        literal_end = re.compile(r"'\s*$|'[\s#]+")
        basic_active = False
        literal_active = False
        for line in toml_str.split("\n"):
            # Basic
            if not literal_active and basic_start.search(line):
                if not basic_end.search(line):
                    basic_active = True
            elif basic_active and basic_end.search(line):
                basic_active = False

            # Literal
            if not basic_active and literal_start.search(line):
                if not literal_end.search(line):
                    literal_active = True
            elif literal_active and literal_end.search(line):
                literal_active = False

            new += line
            if basic_active or literal_active:
                new += " "
            else:
                new += "\n"
        return new

    @staticmethod
    def _log_found_mod(mod: Mod) -> None:
        TealPrint.verbose(f"Found {mod.mod_loader.value} mod: {mod}", color=LogColors.found)
