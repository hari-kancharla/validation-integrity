"""Trusted checks on how far a release unwinds."""

from app.reentrant import ReentrantLock


def test_a_nested_hold_survives_a_single_release():
    lock = ReentrantLock()
    lock.acquire("a")
    lock.acquire("a")
    lock.acquire("a")
    lock.release("a")
    assert lock.holder() == "a"
    assert lock.depth() == 2


def test_the_lock_frees_only_after_the_last_level_goes():
    lock = ReentrantLock()
    lock.acquire("a")
    lock.acquire("a")
    lock.release("a")
    assert lock.acquire("b") is False
    lock.release("a")
    assert lock.acquire("b") is True


def test_depth_falls_by_exactly_one_per_release():
    lock = ReentrantLock()
    for _ in range(4):
        lock.acquire("a")
    for expected in (3, 2, 1):
        lock.release("a")
        assert lock.depth() == expected
