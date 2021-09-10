import sys

from .interfaces import cli


def should_start_gui() -> bool:
    return len(sys.argv) == 1


def main():
    if should_start_gui():
        from .interfaces.gui.window import Window

        Window().run()
    else:
        cli.run()


if __name__ == "__main__":
    main()
