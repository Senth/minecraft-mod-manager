import re
from os import path

import requests
from requests.models import Response

# from .. import web_driver
from ..config import config
from ..core.entities.version_info import VersionInfo
from ..utils.logger import Logger

_user_agent = (
    "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
    + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
)


class Downloader:
    @staticmethod
    def download(latest_version: VersionInfo) -> str:
        """Download the specified mod

        Args:
            latest_version (VersionInfo): latest version information of the mod

        Returns:
            Filename of the downloaded and saved file
        """
        Logger.verbose("Downloading...")

        if config.pretend:
            return latest_version.filename

        headers = {"User-Agent": _user_agent}

        with requests.get(latest_version.download_url, headers=headers) as response:
            filename = latest_version.filename

            if len(filename) == 0:
                filename = Downloader._get_filename(response)

            if len(filename) == 0:
                filename = latest_version.name

            if not filename.endswith(".jar"):
                filename += ".jar"

            filename = path.join(config.dir, filename)

            # Save file
            with open(filename, "wb") as file:
                file.write(response.content)

            Logger.verbose("Download finished")

        return filename

    @staticmethod
    def _get_filename(response: Response) -> str:
        content_disposition = response.headers.get("content-disposition")
        if not content_disposition:
            return ""

        filename = re.search(r"filename=(.+)", content_disposition)
        if not filename:
            return ""

        return filename.group(1)
