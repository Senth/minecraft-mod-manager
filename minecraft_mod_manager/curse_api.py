from os import stat
import requests
from selenium.webdriver.chrome.webdriver import WebDriver
from .mod import Mod, RepoTypes
from .config import config
from .logger import Logger
from .mod_not_found_exception import ModNotFoundException
from .version_info import VersionInfo
from . import web_driver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from typing import List
import re


class CurseApi:
    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver

    def get_latest_version(self, mod: Mod) -> VersionInfo:
        """Get latest version Filtering out alpha and beta releases if necessary.

        Returns:
            VersionInfo or None: Latest version or None if none was found

        Raises:

        """
        self._driver.get(mod.get_parse_url())
        try:
            version_elements: List[WebElement] = self._driver.find_elements_by_xpath(
                './/table[contains(@class, "listing")]/tbody/tr'
            )

            for version_element in version_elements:
                # Get release type
                release_element: WebElement = version_element.find_element_by_xpath(
                    "td[1]/div/span"
                )
                release = release_element.get_attribute("innerText")

                # Get name
                name_element: WebElement = version_element.find_element_by_xpath(
                    "td[2]/a"
                )
                name = name_element.get_attribute("innerText")

                # Uploaded
                uploaded_element: WebElement = version_element.find_element_by_xpath(
                    "td[4]/abbr"
                )
                upload_time = int(uploaded_element.get_attribute("data-epoch"))

                # Get Minecraft Version
                minecraft_version_element: WebElement = (
                    version_element.find_element_by_xpath("td[5]/div/div")
                )
                minecraft_version = minecraft_version_element.get_attribute("innerText")

                # Get file id
                download_element: WebElement = version_element.find_element_by_xpath(
                    "td[7]/div/a[1]"
                )
                href = download_element.get_attribute("href")
                match = re.search(r"download\/(\d{7})", href)
                file_id = int(match.group(1))

                # Get project id
                project_id_container = self._driver.find_element_by_xpath(
                    './/span[contains(text(), "Project ID")]/../span[2]'
                )
                project_id = int(project_id_container.get_attribute("innerText"))

                # All version are older than the installed, no need to continue
                if upload_time < mod.upload_time:
                    return None

                # Checks release type, minecraft version, etc
                if CurseApi._passed_filters(release, minecraft_version):
                    download_url = CurseApi._get_download_url(project_id, file_id)
                    filename = CurseApi._get_filename(download_url)
                    version_info = VersionInfo(
                        release_type=release,
                        name=name,
                        upload_time=upload_time,
                        minecraft_version=minecraft_version,
                        download_url=download_url,
                        filename=filename,
                    )

                    Logger.debug(f"Found CurseForge version {version_info}")
                    return version_info
        except NoSuchElementException:
            raise ModNotFoundException(mod)

        return None

    @staticmethod
    def _get_filename(download_url: str) -> str:
        match = re.search(r".*\/(.*)", download_url)
        return match.group(1)

    @staticmethod
    def _get_download_url(project_id: int, file_id: int) -> str:
        response = requests.get(
            f"https://addons-ecs.forgesvc.net/api/v2/addon/{project_id}/file/{file_id}/download-url",
            allow_redirects=True,
            headers={
                "User-Agent": web_driver.user_agent,
            },
        )

        return response.text

    @staticmethod
    def _passed_filters(release_type: str, minecraft_version: str) -> bool:
        return CurseApi._passed_alpha_beta_filter(
            release_type
        ) and CurseApi._is_set_minecraft_version(minecraft_version)

    @staticmethod
    def _passed_alpha_beta_filter(release_type: str) -> bool:
        if config.alpha:
            return True
        elif config.beta and release_type != "A":
            return True
        elif release_type == "R":
            return True

        return False

    @staticmethod
    def _is_set_minecraft_version(minecraft_version: str) -> bool:
        if not config.minecraft_version:
            return True
        elif config.minecraft_version == minecraft_version:
            return True

        return False
