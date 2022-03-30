import re
import time
from os import path
from typing import Any

import latest_user_agents
import requests
from requests.models import Response
from tealprint import TealPrint

from ..config import config
from ..core.errors.download_failed import DownloadFailed

_headers = {"User-Agent": latest_user_agents.get_random_user_agent()}


class MaxRetriesExceeded(Exception):
    def __init__(self, url: str, retries: int, status_code: int, reason: str, content: str):
        self.url = url
        self.retries = retries
        self.status_code = status_code
        self.reason = reason
        self.content = content

    def __str__(self) -> str:
        return f"{self.status_code}: {self.reason}"


class Downloader:
    retries_max = 5
    retry_backoff_factor = 1.5

    def get(self, url: str) -> Any:
        with Downloader._get_with_retries(url) as response:
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

        with Downloader._get_with_retries(url) as response:
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
    def _get_with_retries(url: str) -> Response:
        response: Response = Response()
        for retry in range(Downloader.retries_max):
            response = requests.get(url, headers=_headers)
            if response.status_code < 500 or response.status_code >= 600:
                return response
            elif retry < Downloader.retries_max:
                response.close()
                delay = Downloader.retry_backoff_factor**retry
                TealPrint.warning(f"{(retry+1)}: Failed to connect to {url}. Retrying in {delay} seconds...")
                time.sleep(delay)
        TealPrint.error(f"{Downloader.retries_max}: Failed to connect to {url}. Giving up.")
        TealPrint.error(f"{response.status_code}: {response.reason}")
        raise MaxRetriesExceeded(
            url, Downloader.retries_max, response.status_code, response.reason, str(response.content)
        )

    @staticmethod
    def _get_filename(response: Response) -> str:
        content_disposition = response.headers.get("content-disposition")
        if not content_disposition:
            return ""

        filename = re.search(r"filename=(.+)", content_disposition)
        if not filename:
            return ""

        return filename.group(1)
