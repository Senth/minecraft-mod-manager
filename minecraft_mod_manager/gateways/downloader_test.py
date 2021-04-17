import builtins
from io import FileIO
from os import path

import pytest
import requests
from mockito import mock, unstub, when
from requests.models import Response
from requests.structures import CaseInsensitiveDict

from ..config import config
from ..core.entities.repo_types import RepoTypes
from ..core.entities.version_info import ReleaseTypes, VersionInfo
from ..gateways.downloader import Downloader


@pytest.fixture
def mock_response():
    mock_response = mock(Response)
    mock_response.content = ""  # type:ignore
    when(mock_response).__enter__(...).thenReturn(mock_response)
    when(mock_response).__exit__(...)
    return mock_response


@pytest.fixture
def mock_file():
    mock_file = mock(FileIO)
    when(mock_file).write(...).thenReturn(0)
    when(mock_file).__enter__(...).thenReturn(mock_file)
    when(mock_file).__exit__(...)
    return mock_file


def test_use_version_info_filename_when_it_exists(mock_file):

    input = VersionInfo(
        release_type=ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Test-mod",
        upload_time=1337,
        minecraft_version="1.16.5",
        download_url="https://test-file",
        filename="some-file.jar",
    )
    expected = path.join(config.dir, input.filename)

    when(requests).get(...).thenReturn(Response())
    when(builtins).open(...).thenReturn(mock_file)
    config.verbose = False
    config.pretend = False

    result = Downloader.download(input)

    unstub()
    assert expected == result


def test_use_name_as_filename_when_no_filename_is_found(mock_file):
    input = VersionInfo(
        release_type=ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Test-mod",
        upload_time=1337,
        minecraft_version="1.16.5",
        download_url="https://test-file",
    )
    expected = path.join(config.dir, input.name + ".jar")

    when(requests).get(...).thenReturn(Response())
    when(builtins).open(...).thenReturn(mock_file)
    config.verbose = False
    config.pretend = False

    result = Downloader.download(input)

    unstub()
    assert expected == result


def test_use_downloaded_filename_when_no_filename_in_version_info(mock_response, mock_file):
    mock_headers = mock(CaseInsensitiveDict)
    mock_response.headers = mock_headers
    input = VersionInfo(
        release_type=ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Test-mod",
        upload_time=1337,
        minecraft_version="1.16.5",
        download_url="https://test-file",
    )
    filename = "downloaded.jar"
    expected = path.join(config.dir, filename)

    when(mock_headers).get(...).thenReturn(f"filename={filename}")
    when(requests).get(...).thenReturn(mock_response)
    when(builtins).open(...).thenReturn(mock_file)
    config.verbose = False
    config.pretend = False

    result = Downloader.download(input)

    unstub()
    assert expected == result


def test_use_downloaded_filename_add_jar_when_no_filename_in_version_info(mock_response, mock_file):
    mock_headers = mock(CaseInsensitiveDict)
    mock_response.headers = mock_headers
    input = VersionInfo(
        release_type=ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Test-mod",
        upload_time=1337,
        minecraft_version="1.16.5",
        download_url="https://test-file",
    )
    filename = "downloaded"
    expected = path.join(config.dir, filename + ".jar")

    when(mock_headers).get(...).thenReturn(f"filename={filename}")
    when(requests).get(...).thenReturn(mock_response)
    when(builtins).open(...).thenReturn(mock_file)
    config.verbose = False
    config.pretend = False

    result = Downloader.download(input)

    unstub()
    assert expected == result


def test_no_mock_interactions_when_pretending():
    input = VersionInfo(
        release_type=ReleaseTypes.stable,
        repo_type=RepoTypes.curse,
        name="Test-mod",
        upload_time=1337,
        minecraft_version="1.16.5",
        download_url="https://test-file",
        filename="file.jar",
    )
    expected = input.filename
    config.verbose = False
    config.pretend = True
    when(requests).get(...).thenRaise(NotImplementedError())
    when(builtins).open(...).thenRaise(NotImplementedError())

    try:
        result = Downloader.download(input)
        assert expected == result
    except Exception as e:
        assert e is None
    finally:
        unstub()
