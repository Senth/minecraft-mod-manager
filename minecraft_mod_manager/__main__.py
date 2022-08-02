import signal

from colored import attr, fg
from tealprint import TealPrint

from .adapters.repo_impl import RepoImpl
from .app.configure.configure import Configure
from .app.install.install import Install
from .app.show.show import Show
from .app.update.update import Update
from .config import config
from .core.entities.actions import Actions
from .gateways.api.mod_finder import ModFinder
from .gateways.arg_parser import parse_args
from .gateways.http import Http
from .gateways.jar_parser import JarParser
from .gateways.sqlite import Sqlite


def signal_handler(signal, frame):
    TealPrint.error("Exiting...", color=fg("yellow") + attr("bold"), exit=True)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    TealPrint.warning(
        "CurseForge has been disabled! See https://github.com/Senth/minecraft-mod-manager for more information."
    )

    args = parse_args()
    config.add_arg_settings(args)

    sqlite = Sqlite()
    jar_parser = JarParser(config.dir)
    http = Http()
    repo = RepoImpl(jar_parser, sqlite, http)
    finder = ModFinder.create(http)
    try:
        if config.action == Actions.update:
            update = Update(repo, finder)
            update.execute(config.arg_mods)

        elif config.action == Actions.install:
            install = Install(repo, finder)
            install.execute(config.arg_mods)

        elif config.action == Actions.configure:
            configure = Configure(repo)
            configure.execute(config.arg_mods)

        elif config.action == Actions.list:
            show = Show(repo)
            show.execute()
    finally:
        sqlite.close()


if __name__ == "__main__":
    main()
