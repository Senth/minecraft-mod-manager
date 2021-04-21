import sys

from ..config import config


class LogColors:
    no_color = "\033[0m"
    red = "\033[91m"
    green = "\033[92m"
    cyan = "\033[96m"
    blue = "\033[94m"
    orange = "\033[31;1m"
    yellow = "\033[33m"
    bold = "\033[1m"

    add = green
    remove = red
    found = cyan
    command = blue
    warning = orange
    skip = yellow


class Logger:
    @staticmethod
    def error(message: str, indent: int = 0, exit: bool = False):
        """Logs a message and prints is at red

        Args:
            message (str): The message to log
            exit (bool): If the program should exit after printing the error
        """
        Logger._print(message, LogColors.red, indent)
        if exit:
            sys.exit(1)

    @staticmethod
    def warning(message: str, indent: int = 0):
        """Logs a message and prints it as orange"""
        Logger._print(message, LogColors.orange, indent)

    @staticmethod
    def info(message: str, color: str = LogColors.no_color, indent: int = 0):
        """Print an information message that always is shown

        Args:
            message (str): The message to log
            color (LogColors): Optional color of the message
        """
        Logger._print(message, color, indent)

    @staticmethod
    def verbose(message: str, color: str = LogColors.no_color, indent: int = 0):
        """Log message if verbose has been set to true

        Args:
            message (str): The message to log
            color (LogColors): Optional color of the message
        """
        if config.verbose:
            Logger._print(message, color, indent)

    @staticmethod
    def debug(message: str, color: str = LogColors.no_color, indent: int = 0):
        """A debug message if --debug has been set to true

        Args:
            message (str): The message to log
            color (LogColors): Optional color of the message
        """
        if config.debug:
            Logger._print(message, color, indent)

    @staticmethod
    def _print(message: str, color: str, indent: int):
        if indent > 0:
            message = "".ljust(indent * 4) + message
        if color == LogColors.no_color:
            print(message)
        else:
            print(f"{color}{message}{LogColors.no_color}")
