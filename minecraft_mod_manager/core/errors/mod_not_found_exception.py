from ...config import config
from ...utils.logger import LogColors, Logger
from ..entities.mod import ModArg


class ModNotFoundException(Exception):
    def __init__(self, mod: ModArg) -> None:
        super()
        self.mod = mod

    def print_message(self) -> None:
        mod_name = self.mod.id

        Logger.info(f"{mod_name}", LogColors.bold)
        Logger.info("Check so that it's slug is correct. You can set the slug by running:", indent=1)
        Logger.info(
            f"{config.app_name} configure {self.mod.id}=curse:mod-slug,modrinth:mod-slug", LogColors.command, indent=1
        )
