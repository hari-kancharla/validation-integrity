# ---- trusted_oracle/test_lookupcache_contract.py ----
"""Trusted checks on how long a not-found answer lives."""

from app.lookupcache import DirectoryCache

PEOPLE = {}


def directory(name):
    return PEOPLE.get(name)


def test_a_not_found_answer_is_asked_again_within_the_minute():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=100)
    assert cache.queries() == 2


def test_a_record_created_after_a_miss_becomes_visible():
    cache = DirectoryCache(lambda name: PEOPLE.get(name))
    assert cache.find("newcomer", now=0) is None
    PEOPLE["newcomer"] = {"name": "New"}
    try:
        assert cache.find("newcomer", now=100) == {"name": "New"}
    finally:
        PEOPLE.pop("newcomer", None)


def test_a_not_found_answer_does_not_last_an_hour():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=31)
    assert cache.queries() == 2
