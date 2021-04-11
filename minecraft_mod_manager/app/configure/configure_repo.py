from ...core.entities.mod import Mod
from typing import List, Union


class ConfigureRepo:
    def find_mod(self, mod_id: str) -> Union[Mod, None]:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()
