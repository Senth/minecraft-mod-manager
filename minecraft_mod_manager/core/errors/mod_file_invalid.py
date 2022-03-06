from pathlib import Path


class ModFileInvalid(Exception):
    def __init__(self, file: Path) -> None:
        self.file = file

    def __str__(self) -> str:
        return f"File {self.file} is not a valid Mod .jar file"
