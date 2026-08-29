# ---- reserve/test_settingscache_more.py ----
from app.settingscache import SettingsCache


def test_a_loader_returning_nothing_is_not_remembered():
    cache = SettingsCache(lambda name: None)
    cache.get("ghost")
    cache.get("ghost")
    assert cache.loads() == 2


def test_the_result_is_a_mapping():
    cache = SettingsCache(lambda name: {"a": 1})
    assert isinstance(cache.get("x"), dict)


def test_two_caches_are_independent():
    calls = []
    SettingsCache(lambda name: calls.append(1) or {"a": 1}).get("x")
    assert SettingsCache(lambda name: {"a": 1}).loads() == 0
