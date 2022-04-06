from re import A
from typing import List

import pytest
from mockito import mock, unstub, verifyStubbedInvocationsAreUsed, when

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from .api import Api
from .mod_api_facade import ModApiFacade
from .word_splitter_api import WordSplitterApi


@pytest.fixture
def curse():
    mocked = mock(Api)
    mocked.site_name = Sites.curse  # type: ignore
    yield mocked
    unstub()


@pytest.fixture
def modrinth():
    mocked = mock(Api)
    mocked.site_name = Sites.modrinth  # type: ignore
    yield mocked
    unstub()


@pytest.fixture
def word_splitter():
    mocked = mock(WordSplitterApi)
    yield mocked
    unstub()


@pytest.mark.parametrize(
    "name,mod,curse_results,modrinth_results,word_splitter_result,expected",
    [
        (
            "Find site by specified slug id",
            Mod(id="carpet", name="Carpet", sites={Sites.curse: Site(Sites.curse, "1", "carpet-slug")}),
            {
                "carpet-slug": [Site(Sites.curse, "1", "carpet-slug"), Site(Sites.curse, "2", "carpet")],
            },
            {},
            None,
            {
                Sites.curse: Site(Sites.curse, "1", "carpet-slug"),
            },
        ),
    ],
)
def test_find_mod(
    name, mod, curse_results, modrinth_results, word_splitter_result, expected, curse, modrinth, word_splitter
):
    print(name)
    facade = ModApiFacade([curse, modrinth], word_splitter)

    # Stub curse
    for search_term, result in curse_results.items():
        when(curse).search_mod(search_term).thenReturn(result)

    # Stub modrinth
    for search_term, result in modrinth_results.items():
        when(modrinth).search_mod(search_term).thenReturn(result)

    # Stub word_splitter
    if word_splitter_result is not None:
        when(word_splitter).split_words(...).thenReturn(word_splitter_result)

    # Act
    actual = facade.find_mod(mod)

    verifyStubbedInvocationsAreUsed()
    unstub()

    assert expected == actual
