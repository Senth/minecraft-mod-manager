from .util.helper import Helper, helper  # lgtm[py/unused-import]


def test_reinstall_mod_after_manual_removal(helper: Helper):
    code = helper.run("install", "carpet")
    carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
    assert carpet_mod is not None
    assert code == 0

    carpet_mod.unlink()

    code = helper.run("install", "carpet")
    carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
    assert carpet_mod is not None
    assert code == 0


def test_install_mod_that_has_no_mod_loader(helper: Helper):
    code = helper.run("install", "jei")
    jei = helper.get_mod_in_dir_like("*jei*.jar")

    assert code == 0
    assert jei is not None


def test_remember_slug_for_installed_mod_if_mod_id_varies(helper: Helper):
    """When installing and supplying a slug it used to save the slug as an id.
    This test makes sure that we actually check what the mod id is before saving
    to the database.
    """
    code = helper.run("install", "unearthed-fabric")

    assert code == 0
    assert helper.exists_in_db("unearthed")
