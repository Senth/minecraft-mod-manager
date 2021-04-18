from typing import Union

from ...core.entities.mod import Mod


class ConfigureRepo:
    def get_mod(self, id: str) -> Union[Mod, None]:
        raise NotImplementedError()

    def update_mod(self, mod: Mod) -> None:
        raise NotImplementedError()
