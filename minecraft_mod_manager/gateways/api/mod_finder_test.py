import pytest
from mockito import mock, unstub, when

from ...core.entities.mod import Mod
from ...core.entities.sites import Site, Sites
from ...core.errors.mod_not_found_exception import ModNotFoundException
from .api import Api
from .mod_finder import ModFinder
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
        (
            "Find both sites when specified by slug id",
            Mod(
                id="carpet",
                name="Carpet",
                sites={
                    Sites.curse: Site(Sites.curse, "1", "carpet-curse"),
                    Sites.modrinth: Site(Sites.modrinth, "a", "carpet-modrinth"),
                },
            ),
            {
                "carpet-curse": [Site(Sites.curse, "1", "carpet-curse"), Site(Sites.curse, "2", "carpet")],
            },
            {
                "carpet-modrinth": [Site(Sites.modrinth, "a", "carpet"), Site(Sites.modrinth, "b", "carpet-modrinth")],
            },
            None,
            {
                Sites.curse: Site(Sites.curse, "1", "carpet-curse"),
                Sites.modrinth: Site(Sites.modrinth, "b", "carpet-modrinth"),
            },
        ),
        (
            "Find both sites when using possible names",
            Mod(id="fabric-api", name="Fabric API"),
            {
                "fabric": [Site(Sites.curse, "1", "carpet-curse"), Site(Sites.curse, "2", "carpet")],
                "api": [Site(Sites.curse, "3", "fabric-api"), Site(Sites.curse, "4", "fubric-api")],
                "fabric-api": [Site(Sites.curse, "5", "febric"), Site(Sites.curse, "6", "fubric")],
            },
            {
                "fabric": [Site(Sites.modrinth, "a", "carpet"), Site(Sites.modrinth, "b", "carpet-modrinth")],
                "api": [Site(Sites.modrinth, "c", "fabric"), Site(Sites.modrinth, "d", "fubric")],
                "fabric-api": [Site(Sites.modrinth, "e", "febric-api"), Site(Sites.modrinth, "f", "fubric-api")],
            },
            None,
            {
                Sites.curse: Site(Sites.curse, "3", "fabric-api"),
                Sites.modrinth: Site(Sites.modrinth, "c", "fabric"),
            },
        ),
        (
            "Use wordsplitter to find id",
            Mod(id="fabricapi", name="Fabric API"),
            {
                "fabricapi": [Site(Sites.curse, "1", "carpet-curse"), Site(Sites.curse, "2", "carpet")],
                "fabric api": [Site(Sites.curse, "3", "fabricapi"), Site(Sites.curse, "4", "fubric-api")],
            },
            {
                "fabricapi": [Site(Sites.modrinth, "a", "carpet"), Site(Sites.modrinth, "b", "carpet-modrinth")],
                "fabric api": [Site(Sites.modrinth, "c", "fabricapi"), Site(Sites.modrinth, "d", "fubric")],
            },
            "fabric api",
            {
                Sites.curse: Site(Sites.curse, "3", "fabricapi"),
                Sites.modrinth: Site(Sites.modrinth, "c", "fabricapi"),
            },
        ),
        (
            "ModNotFoundException when mod couldn't be found to find id",
            Mod(id="fabricapi", name="Fabric API"),
            {
                "fabricapi": [Site(Sites.curse, "1", "carpet-curse"), Site(Sites.curse, "2", "carpet")],
                "fabric api": [Site(Sites.curse, "3", "fabric-api"), Site(Sites.curse, "4", "fubric-api")],
            },
            {
                "fabricapi": [Site(Sites.modrinth, "a", "carpet"), Site(Sites.modrinth, "b", "carpet-modrinth")],
                "fabric api": [Site(Sites.modrinth, "c", "fabric-api"), Site(Sites.modrinth, "d", "fubric")],
            },
            "fabric api",
            ModNotFoundException,
        ),
    ],
)
def test_find_mod(
    name, mod, curse_results, modrinth_results, word_splitter_result, expected, curse, modrinth, word_splitter
):
    print(name)
    finder = ModFinder([curse, modrinth], word_splitter)

    # Stub curse
    for search_term, result in curse_results.items():
        when(curse).search_mod(search_term).thenReturn(result)

    # Stub modrinth
    for search_term, result in modrinth_results.items():
        when(modrinth).search_mod(search_term).thenReturn(result)

    # Stub word_splitter
    if word_splitter_result is not None:
        when(word_splitter).split_words(...).thenReturn(word_splitter_result)

    if expected == ModNotFoundException:
        with pytest.raises(ModNotFoundException):
            finder.find_mod(mod)
    else:
        actual = finder.find_mod(mod)
        assert expected == actual

    unstub()
