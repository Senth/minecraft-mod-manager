import minecraft_mod_manager.config


class LogColors:
    no_color = "\033[0m"
    red = "\033[91m"
    green = "\033[92m"
    cyan = "\033[96m"
    blue = "\033[94m"
    yellow = "\033[33m"

    add = green
    remove = red
    found = cyan


class Logger:
    @staticmethod
    def error(message: str):
        """Logs a message and prints is at red

        Args:
            message (str): The message to log
        """
        print(f"{LogColors.red}{message}{LogColors.no_color}")

    @staticmethod
    def info(message: str, color: str = LogColors.no_color):
        """Log message if verbose has been set to true

        Args:
            message (str): The message to log
            color (LogColors): Optional color of the message
        """
        if minecraft_mod_manager.config.config.verbose:
            if color == LogColors.no_color:
                print(message)
            else:
                print(f"{color}{message}{LogColors.no_color}")

    @staticmethod
    def debug(message: str, color: str = LogColors.no_color):
        """A debug message if --debug has been set to true

        Args:
            message (str): The message to log
            color (LogColors): Optional color of the message
        """
        if minecraft_mod_manager.config.config.debug:
            if color == LogColors.no_color:
                print(message)
            else:
                print(f"{color}{message}{LogColors.no_color}")
