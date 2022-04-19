import builtins
from io import FileIO
from os import path

import pytest
import requests
from mockito import mock, unstub, when
from requests.models import Response

from ..config import config
from ..core.errors.download_failed import DownloadFailed
from .http import Http, MaxRetriesExceeded


@pytest.fixture
def response():
    response = Response()
    response.status_code = 200
    response.encoding = "UTF-8"
    response._content = b""  # type:ignore
    return response


@pytest.fixture
def mock_response():
    response = mock(Response)
    response.status_code = 200  # type:ignore
    response.content = ""  # type:ignore
    when(response).__enter__(...).thenReturn(response)
    when(response).__exit__(...)
    return response


@pytest.fixture
def mock_file():
    mock_file = mock(FileIO)
    when(mock_file).write(...).thenReturn(0)
    when(mock_file).__enter__(...).thenReturn(mock_file)
    when(mock_file).__exit__(...)
    return mock_file


@pytest.fixture
def http():
    return Http()


def test_use_filename_when_it_exists(http, response, mock_file):
    filename = "some-file.jar"
    expected = path.join(config.dir, filename)

    when(requests).get(...).thenReturn(response)
    when(builtins).open(...).thenReturn(mock_file)

    actual = http.download("", filename)

    unstub()
    assert expected == actual


def test_use_downloaded_filename_when_no_filename_specified(http, response, mock_file):
    filename = "downloaded.jar"
    expected = path.join(config.dir, filename)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    when(requests).get(...).thenReturn(response)
    when(builtins).open(...).thenReturn(mock_file)

    actual = http.download("", "")

    unstub()
    assert expected == actual


def test_use_downloaded_filename_add_jar_when_no_filename_specified(http, response, mock_file):
    filename = "downloaded.jar"
    expected = path.join(config.dir, filename)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    when(requests).get(...).thenReturn(response)
    when(builtins).open(...).thenReturn(mock_file)

    actual = http.download("", "")

    unstub()
    assert expected == actual


def test_no_mock_interactions_when_pretending(http):
    filename = "file.jar"
    expected = filename
    config.pretend = True
    when(requests).get(...).thenRaise(NotImplementedError())
    when(builtins).open(...).thenRaise(NotImplementedError())

    try:
        actual = http.download("", filename)
        assert expected == actual
    except Exception as e:
        assert e is None
    finally:
        config.pretend = False
        unstub()


def test_get_when_non_strict_json(http, response):
    response.headers["Content-Type"] = "application/json"
    response._content = '\n{"text":"This is\nmy text"}'.encode("UTF-8")
    expected = {"text": "This is\nmy text"}
    when(requests).get(...).thenReturn(response)

    actual = http.get("https://test.com")

    assert expected == actual

    unstub()


def test_get_when_response_is_string(http, response):
    response.headers["Content-Type"] = "text/plain"
    expected = "This is my text"
    response._content = b"This is my text"  # type:ignore
    when(requests).get(...).thenReturn(response)

    actual = http.get("https://test.com")

    assert expected == actual


def test_get_when_content_type_is_missing(http, response):
    expected = "This is my text"
    response._content = b"This is my text"  # type:ignore
    when(requests).get(...).thenReturn(response)

    actual = http.get("https://test.com")

    assert expected == actual


def test_download_failed(http, response):
    response.status_code = 404  # type:ignore
    response.reason = "Not found"  # type:ignore
    response._content = "404 not found"  # type:ignore
    when(requests).get(...).thenReturn(response)

    with pytest.raises(DownloadFailed):
        http.download("", "")

    unstub()


def test_download_retry(http, mock_response):
    mock_response.status_code = 524  # type:ignore
    mock_response.reason = "Timed out"  # type:ignore
    mock_response._content = "524 Timed out"  # type:ignore
    when(mock_response).close(...)
    when(requests).get(...).thenReturn(mock_response)

    with pytest.raises(MaxRetriesExceeded):
        http.download("", "")

    unstub()
