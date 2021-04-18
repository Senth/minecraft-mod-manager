from typing import Any, List, Literal

from .core.entities.mod import ModArg

_app_name = __package__.replace("_", "-")


class Config:
    def __init__(self):
        self.app_name: str = _app_name
        self.verbose: bool = False
        self.debug: bool = False
        self.pretend: bool = False
        self.dir: str = "."
        self.minecraft_version: str or None
        self.beta: bool = False
        self.alpha: bool = False
        self.action: Literal["install", "update", "configure", "list"]
        self.arg_mods: List[ModArg] = []

    def add_arg_settings(self, args: Any):
        """Set additional configuration from script arguments

        args:
            args (list): All the parsed arguments
        """
        self.action = args.action
        self.pretend = args.pretend
        self.verbose = args.verbose
        self.debug = args.debug
        self.minecraft_version = args.minecraft_version
        self.beta = args.allow_beta
        self.alpha = args.allow_alpha

        if args.debug:
            self.verbose = True

        if args.dir:
            self.dir = args.dir

        if args.allow_alpha:
            self.beta = True

        self.arg_mods = args.mods


global config
config = Config()
