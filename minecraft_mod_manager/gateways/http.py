import re
import time
from os import path
from typing import Any, Dict

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


class Http:
    retries_max = 5
    retry_backoff_factor = 1.5

    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}

    def get(self, url: str) -> Any:
        if url in self.cache:
            return self.cache[url]

        with Http._get_with_retries(url) as response:
            content_type = response.headers.get("Content-Type", "plain/text")
            # Check if headers is json
            if content_type.startswith("application/json"):
                self.cache[url] = response.json(strict=False)
            else:
                self.cache[url] = response.text
            return self.cache[url]

    def download(self, url: str, filename: str) -> str:
        """Download the specified mod
        Returns:
            Filename of the downloaded and saved file
        Exception:
            DownloadFailed if the download failed
        """

        if config.pretend:
            return filename

        with Http._get_with_retries(url) as response:
            if response.status_code != 200:
                raise DownloadFailed(response.status_code, response.reason, str(response.content))

            if len(filename) == 0:
                filename = Http._get_filename(response)

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
        for retry in range(Http.retries_max):
            response = requests.get(url, headers=_headers)
            if response.status_code < 500 or response.status_code >= 600:
                return response
            elif retry < Http.retries_max:
                response.close()
                delay = Http.retry_backoff_factor**retry
                TealPrint.warning(f"{(retry+1)}: Failed to connect to {url}. Retrying in {delay} seconds...")
                time.sleep(delay)
        TealPrint.error(f"{Http.retries_max}: Failed to connect to {url}. Giving up.")
        TealPrint.error(f"{response.status_code}: {response.reason}")
        raise MaxRetriesExceeded(url, Http.retries_max, response.status_code, response.reason, str(response.content))

    @staticmethod
    def _get_filename(response: Response) -> str:
        content_disposition = response.headers.get("content-disposition")
        if not content_disposition:
            return ""

        filename = re.search(r"filename=(.+)", content_disposition)
        if not filename:
            return ""

        return filename.group(1)
