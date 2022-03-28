from tealprint import TealPrint

from ...config import config
from ...utils.log_colors import LogColors
from ..entities.mod import ModArg


class ModNotFoundException(Exception):
    def __init__(self, mod: ModArg) -> None:
        self.mod = mod

    def print_message(self) -> None:
        mod_name = self.mod.id

        TealPrint.info(f"{mod_name}", color=LogColors.header, push_indent=True)
        TealPrint.info("Check so that it's slug is correct. You can set the slug by running:")
        TealPrint.info(
            f"{config.app_name} configure {self.mod.id}=curse:mod-slug,modrinth:mod-slug",
            color=LogColors.command,
            pop_indent=True,
        )
