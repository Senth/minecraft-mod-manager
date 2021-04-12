from typing import Sequence

from ...core.entities.mod import ModArg
from ..download.download import Download
from .update_repo import UpdateRepo


class Update(Download):
    def __init__(self, repo: UpdateRepo) -> None:
        super().__init__(repo, "Updated")
        self._repo = repo

    def execute(self, mods: Sequence[ModArg]) -> None:
        # Use all installed mods if mods is empty
        if len(mods) == 0:
            mods = self._repo.get_all_mods()

        downloads = self._find_latest_versions(mods)
        self._download_and_install(downloads)
