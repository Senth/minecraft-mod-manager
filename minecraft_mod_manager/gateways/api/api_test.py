import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.errors.mod_not_found_exception import ModNotFoundException
from ...gateways.downloader import Downloader
from .api import Api


@pytest.fixture
def downloader():
    mocked = mock(Downloader)
    yield mocked
    unstub()


@pytest.fixture
def api(downloader):
    return Api(downloader)


def test_find_mod_id_use_slug_directly_when_available(api: Api):
    when(api)._find_mod_id_by_slug("slug", set(["slug"])).thenReturn(("id", "slug"))

    expected = "id"
    input = Mod("", "", site_slug="slug")
    result = api._find_mod_id(input)

    verifyStubbedInvocationsAreUsed()

    assert result == expected


def test_find_mod_id_from_mod_id(api: Api):
    when(api)._find_mod_id_by_slug(...).thenReturn(("id", "mod-id"))

    expected_id = "id"
    expected_mod = Mod("mod-id", "", site_slug="mod-id")
    mod = Mod("mod-id", "")
    result = api._find_mod_id(mod)

    verifyStubbedInvocationsAreUsed()

    assert expected_id == result
    assert expected_mod == mod


def test_mod_not_found_uses_all_possible_names(api: Api):
    input = Mod("mod-id", "", file="some-filename")

    when(api)._find_mod_id_by_slug("mod-id", input.get_possible_slugs())
    when(api)._find_mod_id_by_slug("some", input.get_possible_slugs())

    with pytest.raises(ModNotFoundException) as e:
        api._find_mod_id(input)

    assert e.type == ModNotFoundException

    verifyStubbedInvocationsAreUsed()
