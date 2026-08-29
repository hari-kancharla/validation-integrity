from app.casematch import SettingsIndex


def test_a_setting_is_found_under_its_own_spelling():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("Timeout") == 30


def test_a_setting_is_found_under_a_different_case():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("TIMEOUT") == 30


def test_an_unrelated_name_is_not_found():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("Retries") is None


def test_a_later_put_overwrites_a_case_variant():
    index = SettingsIndex()
    index.put("Timeout", 30)
    index.put("timeout", 60)
    assert index.get("TimeOut") == 60


def test_the_first_spelling_is_the_one_reported():
    index = SettingsIndex()
    index.put("Timeout", 30)
    index.put("TIMEOUT", 60)
    assert index.names() == ["Timeout"]


def test_a_missing_name_returns_the_default():
    assert SettingsIndex().get("nothing", "fallback") == "fallback"


def test_a_sharp_s_is_its_own_name():
    """Setting names come from our own catalogue, which spells them one way only."""
    index = SettingsIndex()
    index.put("gro" + chr(0x00DF) + "e", 1)
    assert index.get("grosse") is None
