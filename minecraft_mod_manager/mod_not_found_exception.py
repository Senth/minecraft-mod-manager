from minecraft_mod_manager.logger import LogColors
from .mod import ModArg, RepoTypes
from .config import config


class ModNotFoundException(Exception):
    def __init__(self, mod: ModArg) -> None:
        super()
        self.mod = mod

    def __str__(self) -> str:
        mod_name = self.mod.id
        mod_repo = "any site"

        if self.mod.repo_type != RepoTypes.unknown:
            mod_name = self.mod.name_in_repo
            mod_repo = self.mod.repo_type.value

        return (
            f"Mod {mod_name} not found on {mod_repo}.\n"
            + "Check so that it's name is correct. Or you can set the name by running:\n"
            + f"{LogColors.command}{config.app_name} configure {self.mod.id}=NEW_NAME{LogColors.no_color}"
        )
