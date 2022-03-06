import re
from os import path
from typing import Any

import latest_user_agents
import requests
from requests.models import Response

from ..config import config
from ..core.errors.download_failed import DownloadFailed

_headers = {"User-Agent": latest_user_agents.get_random_user_agent()}


class Downloader:
    def get(self, url: str) -> Any:
        headers = _headers

        with requests.get(url, headers=headers) as response:
            return response.json(strict=False)

    def download(self, url: str, filename: str) -> str:
        """Download the specified mod
        Returns:
            Filename of the downloaded and saved file
        Exception:
            DownloadFailed if the download failed
        """

        if config.pretend:
            return filename

        with requests.get(url, headers=_headers) as response:
            if response.status_code != 200:
                raise DownloadFailed(response.status_code, response.reason, str(response.content))

            if len(filename) == 0:
                filename = Downloader._get_filename(response)

            if not filename.endswith(".jar"):
                filename += ".jar"

            filename = path.join(config.dir, filename)

            # Save file
            with open(filename, "wb") as file:
                file.write(response.content)

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
