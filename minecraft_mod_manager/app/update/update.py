from typing import List, Sequence

from ...core.entities.mod import Mod, ModArg
from ..download.download import Download
from .update_repo import UpdateRepo


class Update(Download):
    def __init__(self, repo: UpdateRepo) -> None:
        super().__init__(repo, "Updated")
        self._repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        mods_to_update: List[Mod] = []

        # Use all installed mods if mods is empty
        if len(mods) == 0:
            mods_to_update = list(self._repo.get_all_mods())
        else:
            for mod_arg in mods:
                mod = self._repo.get_mod(mod_arg.id)
                if mod:
                    mods_to_update.append(mod)

        self.find_download_and_install(mods_to_update)
