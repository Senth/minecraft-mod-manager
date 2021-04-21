from .adapters.repo_impl import RepoImpl
from .app.configure.configure import Configure
from .app.install.install import Install
from .app.show.show import Show
from .app.update.update import Update
from .config import config
from .core.entities.actions import Actions
from .gateways.arg_parser import parse_args
from .gateways.downloader import Downloader
from .gateways.jar_parser import JarParser
from .gateways.sqlite import Sqlite


def main():
    args = parse_args()
    config.add_arg_settings(args)

    sqlite = Sqlite()
    jar_parser = JarParser(config.dir)
    downloader = Downloader()
    repo = RepoImpl(jar_parser, sqlite, downloader)
    try:
        if config.action == Actions.update:
            update = Update(repo)
            update.execute(config.arg_mods)

        elif config.action == Actions.install:
            install = Install(repo)
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
