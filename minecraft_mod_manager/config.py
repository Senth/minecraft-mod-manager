from os import path
import re
from typing import Any, List, Literal, Tuple
import argparse
from .mod import ModArg, RepoTypes

_app_name = __package__.replace("_", "-")

_red_color = "\033[91m"
_no_color = "\033[0m"


def _is_dir(dir: str) -> str:
    if path.isdir(dir):
        return dir
    else:
        raise NotADirectoryError(dir)


class Config:
    def __init__(self):
        self._set_default_values()
        self._parse_args()
        self.app_name: str = _app_name
        self.verbose: bool
        self.debug: bool
        self.pretend: bool
        self.dir: str
        self.minecraft_version: str or None
        self.beta: bool
        self.alpha: bool
        self.action: Literal["install", "update"]
        self.mods: List[ModArg]

    def _parse_args(self):
        # Get arguments first to get verbosity before we get everything else
        parser = argparse.ArgumentParser(
            description="Install or update Minecraft mods from Curseforge"
        )

        parser.add_argument(
            "action",
            choices=["install", "update", "configure", "list"],
            help="Install, update, configure, or list mods",
        )
        parser.add_argument(
            "mods",
            nargs="*",
            help="The mods to install, update, or configure. If no mods are specified during an update, all mods will be updated. "
            + "\nTo specify the download site for the mod you can put 'site:' before the mod. E.g. 'curse:litematica' "
            + "By default it searches all sites for the mod.\nTo configure an alias for the mod, use 'mod_name=ALIAS_NAME'."
            + "E.g. 'dynmap=dynmapforge'",
        )
        parser.add_argument(
            "-d",
            "--dir",
            type=_is_dir,
            help="Location of the mods folder. By default it's the current directory",
        )
        parser.add_argument(
            "-v",
            "--minecraft-version",
            help="Only update mods to this Minecraft version",
        )
        parser.add_argument(
            "--allow-beta",
            action="store_true",
            help="Allow beta releases",
        )
        parser.add_argument(
            "--allow-alpha",
            action="store_true",
            help="Allow alpha and beta releases",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Print more messages",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Turn on debug messages. This automatically turns on --verbose as well",
        )
        parser.add_argument(
            "--pretend",
            action="store_true",
            help="Only pretend to update/configure. Does not change anything",
        )

        _args = parser.parse_args()
        self._add_args_settings(_args)

    def _add_args_settings(self, args: Any):
        """Set additional configuration from script arguments

        Args:
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

        # Process mods
        self.mods = []

        for mod_arg in args.mods:
            match = re.match(r"(?:(.+):)?([\w-]+)(?:=(.+))?", mod_arg)

            if not match:
                print(f"{_red_color}Invalid mod syntax: {mod_arg}{_no_color}")
                exit(1)

            repo_type_name, mod_id, repo_alias = match.groups()
            if repo_type_name and len(repo_type_name) > 0:
                try:
                    repo_type = RepoTypes[repo_type_name.lower()]
                except KeyError:
                    print(f"{_red_color}No site named {repo_type_name}{_no_color}")
                    print(f"Valid names are:")
                    for enum in RepoTypes:
                        print(f"{enum.value}")

                    exit(1)
            else:
                repo_type = RepoTypes.unknown

            if not repo_alias:
                repo_alias = mod_id

            self.mods.append(ModArg(repo_type, mod_id, repo_alias))

    def _set_default_values(self):
        """Set default values for variables"""
        self.dir = "."


global config
config = Config()
