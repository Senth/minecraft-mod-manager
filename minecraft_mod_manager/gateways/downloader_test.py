import builtins
from io import FileIO
from os import path

import pytest
import requests
from mockito import mock, unstub, when
from requests.models import Response
from requests.structures import CaseInsensitiveDict

from ..config import config
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


@pytest.fixture
def downloader():
    return Downloader()


def test_use_filename_when_it_exists(downloader, mock_file):
    filename = "some-file.jar"
    expected = path.join(config.dir, filename)

    when(requests).get(...).thenReturn(Response())
    when(builtins).open(...).thenReturn(mock_file)

    result = downloader.download("", filename)

    unstub()
    assert expected == result


def test_use_downloaded_filename_when_no_filename_specified(downloader, mock_response, mock_file):
    mock_headers = mock(CaseInsensitiveDict)
    mock_response.headers = mock_headers
    filename = "downloaded.jar"
    expected = path.join(config.dir, filename)

    when(mock_headers).get(...).thenReturn(f"filename={filename}")
    when(requests).get(...).thenReturn(mock_response)
    when(builtins).open(...).thenReturn(mock_file)

    result = downloader.download("", "")

    unstub()
    assert expected == result


def test_use_downloaded_filename_add_jar_when_no_filename_specified(downloader, mock_response, mock_file):
    mock_headers = mock(CaseInsensitiveDict)
    mock_response.headers = mock_headers
    filename = "downloaded"
    expected = path.join(config.dir, filename + ".jar")

    when(mock_headers).get(...).thenReturn(f"filename={filename}")
    when(requests).get(...).thenReturn(mock_response)
    when(builtins).open(...).thenReturn(mock_file)

    result = downloader.download("", "")

    unstub()
    assert expected == result


def test_no_mock_interactions_when_pretending(downloader):
    filename = "file.jar"
    expected = filename
    config.pretend = True
    when(requests).get(...).thenRaise(NotImplementedError())
    when(builtins).open(...).thenRaise(NotImplementedError())

    try:
        result = downloader.download("", filename)
        assert expected == result
    except Exception as e:
        assert e is None
    finally:
        config.pretend = False
        unstub()
