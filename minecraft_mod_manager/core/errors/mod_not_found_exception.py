from ...config import config
from ...utils.logger import LogColors
from ..entities.mod import ModArg, Sites


class ModNotFoundException(Exception):
    def __init__(self, mod: ModArg) -> None:
        super()
        self.mod = mod

    def __str__(self) -> str:
        mod_name = self.mod.id
        mod_repo = "any site"

        if self.mod.site != Sites.unknown:
            mod_name = self.mod.site_slug
            mod_repo = self.mod.site.value

        return (
            f"Mod {mod_name} not found on {mod_repo}.\n"
            + "Check so that it's name is correct. Or you can set the name by running:\n"
            + f"{LogColors.command}{config.app_name} configure {self.mod.id}=NEW_NAME{LogColors.no_color}"
        )
