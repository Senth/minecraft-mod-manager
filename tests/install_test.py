import pytest

from .util.helper import Helper


@pytest.fixture
def helper():
    helper = Helper()
    yield helper
    helper.unstub()


# TODO CurseForge disabled for now
# def test_reinstall_mod_after_manual_removal(helper: Helper):
#     code = helper.run("install", "carpet")
#     carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
#     assert carpet_mod is not None
#     assert code == 0

#     carpet_mod.unlink()

#     code = helper.run("install", "carpet")
#     carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
#     assert carpet_mod is not None
#     assert code == 0


# def test_install_mod_that_has_no_mod_loader(helper: Helper):
#     code = helper.run("install", "jei")
#     jei = helper.get_mod_in_dir_like("*jei*.jar")

#     assert code == 0
#     assert jei is not None


# def test_remember_slug_for_installed_mod_if_mod_id_varies(helper: Helper):
#     """When installing and supplying a slug it used to save the slug as an id.
#     This test makes sure that we actually check what the mod id is before saving
#     to the database.
#     """
#     code = helper.run("install", "unearthed-fabric")

#     assert code == 0
#     assert helper.exists_in_db("unearthed")


def test_install_from_modrinth(helper: Helper):
    code = helper.run("install", "lithium=modrinth:lithium")
    lithium_mod = helper.get_mod_in_dir_like("*lithium*.jar")

    assert lithium_mod is not None
    assert code == 0


# TODO CurseForge disabled for now
# def test_install_entity_culling_when_using_word_splitter(helper: Helper):
#     """Tests to make sure that the word splitter is working correctly.
#     Some mods have names that makes them hard to search for on both Curse and
#     Modrinth. This test makes sure that we can search for those mods.
#     """
#     code = helper.run("install", "entityculling")
#     entity_culling = helper.get_mod_in_dir_like("*entityculling*.jar")

#     assert code == 0
#     assert entity_culling is not None


# def test_install_dependencies(helper: Helper):
#     """Tests that dependencies are installed correctly."""
#     code = helper.run("install", "lambdabettergrass")
#     lamba_better_crass = helper.get_mod_in_dir_like("lambdabettergrass*.jar")
#     dependency_fabric_api = helper.get_mod_in_dir_like("fabric-api*.jar")

#     assert code == 0
#     assert lamba_better_crass is not None
#     assert dependency_fabric_api is not None


def test_install_dcch(helper: Helper):
    code = helper.run("install", "dcch")
    dcch = helper.get_mod_in_dir_like("DCCH*.jar")

    assert code == 0
    assert dcch is not None
