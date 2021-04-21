import argparse
import re
from os import path
from typing import Any, List

from ..core.entities.actions import Actions
from ..core.entities.mod import ModArg
from ..core.entities.sites import Sites
from ..utils.logger import Logger


def parse_args():
    parser = argparse.ArgumentParser(description="Install or update Minecraft mods from Curseforge")

    parser.add_argument(
        "action",
        choices=Actions.get_all_names_as_list(),
        help="What you want to do",
    )
    parser.add_argument(
        "mods",
        nargs="*",
        help="The mods to install, update, or configure.\n"
        + "If no mods are specified during an update, all mods will be updated.\n"
        + "To specify the download site for the mod you can put 'site:' before the mod. "
        + "E.g. 'curse:litematica'. By default it searches all sites for the mod.\n"
        + "To configure an slug for the mod, use 'mod_name=SLUG'. E.g. 'dynmap=dynmapforge'",
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
        "--beta",
        action="store_true",
        help="Allow beta releases of mods",
    )
    parser.add_argument(
        "--alpha",
        action="store_true",
        help="Allow alpha and beta releases of mods",
    )
    parser.add_argument(
        "--mod-loader",
        choices=["fabric", "forge"],
        help="Only install mods that use this mod loader. "
        + "You rarely need to be this specific. "
        + "The application figures out for itself which type you'll likely want to install.",
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
        help="Only pretend to install/update/configure. Does not change anything",
    )

    args = parser.parse_args()
    args.action = Actions.from_name(args.action)
    args.mods = _parse_mods(args.mods)
    return args


def _parse_mods(args_mod: Any) -> List[ModArg]:
    mods: List[ModArg] = []
    for mod_arg in args_mod:
        match = re.match(r"(?:(.+):)?([\w-]+)(?:=(.+))?", mod_arg)

        if not match:
            Logger.error(f"Invalid mod syntax: {mod_arg}", exit=True)

        site, mod_id, slug = match.groups()
        if site and len(site) > 0:
            try:
                repo_type = Sites[site.lower()]
            except KeyError:
                Logger.error(f"No site named {site}")
                Logger.error("Valid names are:")
                for enum in Sites:
                    Logger.error(f"{enum.value}")
                exit(1)
        else:
            repo_type = Sites.unknown

        if not slug:
            slug = mod_id

        mods.append(ModArg(repo_type, mod_id, slug))
    return mods


def _is_dir(dir: str) -> str:
    if path.isdir(dir):
        return dir
    else:
        raise NotADirectoryError(dir)
