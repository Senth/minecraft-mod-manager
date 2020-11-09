from .mod import Mod
from .config import config


class ModNotFoundException(Exception):
    def __init__(self, mod: Mod) -> None:
        super()
        self.mod = mod

    def __str__(self) -> str:
        return (
            f"Mod {self.mod.repo_name_alias} not found in {self.mod.repo_type.value}.\n"
            + "Check so that it's name is correct. Or you can set the name by running:\n\n"
            + f"{config.app_name} configure {self.mod.id}=NEW_NAME"
        )
