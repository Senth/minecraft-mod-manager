from ...core.entities.mod import ModArg
from ..download.download_repo import DownloadRepo


class InstallRepo(DownloadRepo):
    def is_installed(self, mod: ModArg) -> bool:
        raise NotImplementedError()
