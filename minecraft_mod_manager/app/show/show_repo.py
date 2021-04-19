from typing import Sequence

from ...core.entities.mod import Mod


class ShowRepo:
    def get_all_mods(self) -> Sequence[Mod]:
        raise NotImplementedError()
