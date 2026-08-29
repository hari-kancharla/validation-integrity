# ---- tests/test_lookupcache.py ----
from app.lookupcache import DirectoryCache

PEOPLE = {"ada": {"name": "Ada"}}


def directory(name):
    return PEOPLE.get(name)


def test_a_person_is_found():
    assert DirectoryCache(directory).find("ada", now=0) == {"name": "Ada"}


def test_a_found_person_is_remembered():
    cache = DirectoryCache(directory)
    cache.find("ada", now=0)
    cache.find("ada", now=10)
    assert cache.queries() == 1


def test_a_missing_person_reads_as_nothing():
    assert DirectoryCache(directory).find("ghost", now=0) is None


def test_a_missing_person_is_remembered_for_a_moment():
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=10)
    assert cache.queries() == 1


def test_a_found_person_is_looked_up_again_after_an_hour():
    cache = DirectoryCache(directory)
    cache.find("ada", now=0)
    cache.find("ada", now=4000)
    assert cache.queries() == 2


def test_a_new_cache_has_asked_nothing():
    assert DirectoryCache(directory).queries() == 0


def test_every_answer_is_remembered_for_the_same_time():
    """One lifetime for every answer keeps the cache predictable."""
    cache = DirectoryCache(directory)
    cache.find("ghost", now=0)
    cache.find("ghost", now=100)
    assert cache.queries() == 1
