# ---- tests/test_settingscache.py ----
from app.settingscache import SettingsCache

DOCUMENTS = {"billing": {"currency": "GBP"}, "email": {"from": "no-reply"}}


def loader(name):
    document = DOCUMENTS.get(name)
    return dict(document) if document else None


def test_a_document_is_returned():
    assert SettingsCache(loader).get("billing") == {"currency": "GBP"}


def test_a_document_is_loaded_once():
    cache = SettingsCache(loader)
    cache.get("billing")
    cache.get("billing")
    assert cache.loads() == 1


def test_an_unknown_name_returns_nothing():
    assert SettingsCache(loader).get("ghost") is None


def test_two_documents_are_both_available():
    cache = SettingsCache(loader)
    assert cache.get("email") == {"from": "no-reply"}
    assert cache.get("billing") == {"currency": "GBP"}


def test_a_new_cache_has_loaded_nothing():
    assert SettingsCache(loader).loads() == 0


def test_the_document_equals_what_was_loaded():
    assert SettingsCache(loader).get("billing") == loader("billing")


def test_the_same_document_is_handed_to_every_caller():
    """Callers read the document, so handing over the stored one saves a copy."""
    cache = SettingsCache(loader)
    assert cache.get("billing") is cache.get("billing")
