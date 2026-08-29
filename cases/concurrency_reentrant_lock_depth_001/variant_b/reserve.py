# ---- reserve/test_reentrant_more.py ----
from app.reentrant import ReentrantLock


def test_a_fresh_lock_names_no_holder():
    assert ReentrantLock().holder() is None


def test_a_fresh_lock_has_no_depth():
    assert ReentrantLock().depth() == 0


def test_a_turned_away_caller_does_not_change_the_depth():
    lock = ReentrantLock()
    lock.acquire("a")
    before = lock.depth()
    lock.acquire("b")
    assert lock.depth() == before


def test_owners_are_compared_by_value():
    lock = ReentrantLock()
    lock.acquire("owner-1")
    assert lock.acquire("owner-" + "1") is True
