# ---- trusted_oracle/test_settingscache_contract.py ----
"""Trusted checks on whether one caller can change another's document."""

from app.settingscache import SettingsCache

DOCUMENTS = {"billing": {"currency": "GBP"}}


def loader(name):
    document = DOCUMENTS.get(name)
    return dict(document) if document else None


def test_a_caller_cannot_change_the_next_callers_document():
    cache = SettingsCache(loader)
    first = cache.get("billing")
    first["currency"] = "USD"
    assert cache.get("billing") == {"currency": "GBP"}


def test_each_caller_gets_its_own_object():
    cache = SettingsCache(loader)
    assert cache.get("billing") is not cache.get("billing")


def test_a_deleted_field_does_not_persist():
    cache = SettingsCache(loader)
    cache.get("billing").clear()
    assert cache.get("billing") == {"currency": "GBP"}
