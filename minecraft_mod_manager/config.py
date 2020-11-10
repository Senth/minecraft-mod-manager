from os import path
from typing import List
import sys
import site
import importlib.util
import argparse
from platform import system
import minecraft_mod_manager.logger

_app_name = __package__.replace("_", "-")
_config_dir = path.join("config", _app_name)
_config_file = path.join(_config_dir, "config.py")
_example_file = path.join(_config_dir, "config.example.py")

# Search for config file in sys path
_user_config_file = path.join(site.getuserbase(), _config_file)
_config_file = ""
if path.exists(_user_config_file):
    _config_file = _user_config_file
# User hasn't configured the program yet
elif system() != "Linux":
    _config_file = _user_config_file
    _sys_config_example = path.join(sys.prefix, _example_file)

    print("This seems like it's the first time you run this program.")
    print(
        f"For this program to work properly you have to configure it by creating '{_config_file}'."
    )
    print(
        "In the same folder there's an example file 'config.example.py' you can copy to 'config.py'."
    )
    print(
        f"It can also be located in {_sys_config_example}. Otherwise you can download the config.example.py from https://github.com/Senth/youtube-series-downloader/tree/main/config and place it in the correct location"
    )
    sys.exit(1)

_spec = importlib.util.spec_from_file_location("config", _user_config_file)
_user_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_user_config)


def _print_missing(variable_name):
    minecraft_mod_manager.logger.Logger.error(
        f"Missing {variable_name} variable in config file: {_config_file}"
    )
    print("Please add it to you config.py again to continue")
    sys.exit(1)


def _is_dir(dir: str) -> str:
    if path.isdir(dir):
        return dir
    else:
        raise NotADirectoryError(dir)


class Config:
    def __init__(self, user_config):
        self._os = system()
        self._user_config = user_config
        self._set_default_values()
        self._get_optional_variables()
        self._check_required_variables()
        self._parse_args()
        self._check_chrome_driver()
        self.app_name: str = _app_name
        self.verbose: bool
        self.debug: bool
        self.pretend: bool
        self.dir: str
        self.minecraft_version: str or None
        self.beta: bool
        self.alpha: bool
        self.action: "install" or "update"
        self.mods: List[str]

    def _parse_args(self):
        # Get arguments first to get verbosity before we get everything else
        parser = argparse.ArgumentParser(
            description="Install or update Minecraft mods from Curseforge"
        )

        parser.add_argument(
            "action",
            choices=["install", "update", "configure"],
            help="Install, update or configure mods",
        )
        parser.add_argument(
            "mods",
            nargs="*",
            help="The mods to install, update, or configure. If no mods are specified during an update, all mods will be updated. "
            + "To select repository type for a mod you can put curse: before the mod e.g. 'curse:litematica'. "
            + "The default repository is curse.",
        )
        parser.add_argument(
            "--verbose", action="store_true", help="Prints out helpful messages."
        )
        parser.add_argument(
            "-p",
            "--pretend",
            action="store_true",
            help="Only pretend to download and update mods.",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Turn on debug messages. This automatically turns on --verbose as well.",
        )
        parser.add_argument(
            "-d",
            "--dir",
            type=_is_dir,
            help="Location of the mods folder. By default it's the current directory.",
        )
        parser.add_argument(
            "-v",
            "--minecraft-version",
            help="Only update mods to this Minecraft version.",
        )
        parser.add_argument(
            "--allow-beta", action="store_true", help="Allow beta releases."
        )
        parser.add_argument(
            "--allow-alpha", action="store_true", help="Allow alpha and beta releases."
        )

        _args = parser.parse_args()
        self._add_args_settings(_args)

    def _add_args_settings(self, args):
        """Set additional configuration from script arguments

        Args:
            args (list): All the parsed arguments
        """
        self.action = args.action
        self.mods = args.mods

        self.verbose = args.verbose
        self.debug = args.debug
        self.pretend = args.pretend

        if args.debug:
            self.verbose = True

        if args.dir:
            self.dir = args.dir

        self.minecraft_version = args.minecraft_version
        self.beta = args.allow_beta
        self.alpha = args.allow_alpha

        if args.allow_alpha:
            self.beta = True

    def _set_default_values(self):
        """Set default values for variables"""
        self.chrome_driver = "/usr/bin/chromedriver"
        self.dir = "."

    def _get_optional_variables(self):
        """Get optional values from the config file"""
        if self._os != "Windows":
            try:
                self.chrome_driver = _user_config.CHROME_DRIVER
            except AttributeError:
                pass

    def _check_required_variables(self):
        """Check that all required variables are set in the user config file"""
        if self._os == "Windows":
            try:
                self.chrome_driver = _user_config.CHROME_DRIVER
            except AttributeError:
                _print_missing("CHROME_DRIVER")

    def _check_chrome_driver(self):
        """Checks the location of the chromedriver"""
        if not path.exists(self.chrome_driver):
            minecraft_mod_manager.logger.Logger.error(
                f"Couldn't find chromedriver in {self.chrome_driver}."
            )
            exit(1)


global config
config = Config(_user_config)
