from ..download.download_repo import DownloadRepo


class InstallRepo(DownloadRepo):
    def is_installed(self, id: str) -> bool:
        raise NotImplementedError()
