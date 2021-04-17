from ..entities.mod import ModArg


class ModAlreadyExists(Exception):
    def __init__(self, mod: ModArg) -> None:
        super()
        self.mod = mod

    def __str__(self) -> str:
        return f"Mod {self.mod.id} already found in the the db.\n"
