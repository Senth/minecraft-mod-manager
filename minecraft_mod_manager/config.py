from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, List, Literal, Union

from .core.entities.mod import ModArg
from .core.entities.mod_loaders import ModLoaders
from .core.entities.version_info import Stabilities


class Config:
    def __init__(self):
        self.app_name: str = __package__.replace("_", "-")
        self.app_report_url: str = (
            "https://github.com/Senth/minecraft-mod-manager/issues/new?labels=bug&template=bug_report.md"
        )
        self.verbose: bool = False
        self.debug: bool = False
        self.pretend: bool = False
        self.dir: Path = Path(".")
        self.action: Literal["install", "update", "configure", "list"]
        self.arg_mods: List[ModArg] = []
        self.filter = Filter()

        try:
            self.app_version: str = version(self.app_name)
        except PackageNotFoundError:
            self.app_version: str = "UNKNOWN"

    def add_arg_settings(self, args: Any):
        """Set additional configuration from script arguments

        args:
            args (list): All the parsed arguments
        """
        self.action = args.action
        self.pretend = args.pretend
        self.verbose = args.verbose
        self.debug = args.debug
        self.arg_mods = args.mods

        if args.debug:
            self.verbose = True

        if args.dir:
            self.dir = Path(args.dir)

        if args.minecraft_version:
            self.filter.version = args.minecraft_version

        if args.alpha:
            self.filter.stability = Stabilities.alpha
        elif args.beta:
            self.filter.stability = Stabilities.beta

        if args.mod_loader:
            self.filter.loader = ModLoaders.from_name(args.mod_loader)


class Filter:
    def __init__(self) -> None:
        self.stability: Stabilities = Stabilities.release
        self.version: Union[str, None] = None
        self.loader: ModLoaders = ModLoaders.unknown


config = Config()
