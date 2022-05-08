import pytest

from .util.helper import Helper


@pytest.fixture
def helper():
    helper = Helper()
    yield helper
    helper.unstub()


# TODO CurseForge disabled for now
# def test_update_does_not_remove_mods(helper: Helper):
#     code = helper.run("install", "carpet", "-v", "1.16.2")
#     carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
#     assert code == 0
#     assert carpet_mod is not None

#     code = helper.run("update")
#     carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
#     assert code == 0
#     assert carpet_mod is not None

#     code = helper.run("update")
#     carpet_mod = helper.get_mod_in_dir_like("*carpet*.jar")
#     assert code == 0
#     assert carpet_mod is not None
