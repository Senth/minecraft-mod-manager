import re
from os import path
from typing import Any

import requests
from requests.models import Response

from ..config import config

_user_agent = (
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
)
_headers = {"User-Agent": _user_agent}


class Downloader:
    def get(self, url: str, user_agent_fix: bool = False) -> Any:
        headers = {}
        if user_agent_fix:
            headers = _headers

        with requests.get(url, headers=headers) as response:
            return response.json(strict=False)

    def download(self, url: str, filename: str) -> str:
        """Download the specified mod
        Returns:
            Filename of the downloaded and saved file
        """

        if config.pretend:
            return filename

        with requests.get(url, headers=_headers) as response:

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
