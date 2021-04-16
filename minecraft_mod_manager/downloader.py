import re
from os import path

import requests
from requests.models import Response

from . import web_driver
from .config import config
from .logger import Logger
from .version_info import VersionInfo


class Downloader:
    @staticmethod
    def download(latest_version: VersionInfo) -> str:
        """Download the specified mod

        Args:
            latest_version (VersionInfo): latest version information of the mod

        Returns:
            Filename of the downloaded and saved file
        """
        Logger.verbose(f"Downloading...")

        if config.pretend:
            return latest_version.filename

        response = requests.get(
            latest_version.download_url,
            headers={
                "User-Agent": web_driver.user_agent,
            },
        )
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

        return filename.group(0)
