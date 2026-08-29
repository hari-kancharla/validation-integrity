# ---- tests/test_reentrant.py ----
from app.reentrant import ReentrantLock


def test_an_unheld_lock_is_taken_by_the_first_caller():
    lock = ReentrantLock()
    assert lock.acquire("a") is True
    assert lock.holder() == "a"


def test_the_owner_may_take_the_lock_again():
    lock = ReentrantLock()
    lock.acquire("a")
    assert lock.acquire("a") is True
    assert lock.depth() == 2


def test_another_owner_is_turned_away():
    lock = ReentrantLock()
    lock.acquire("a")
    assert lock.acquire("b") is False
    assert lock.holder() == "a"


def test_a_single_level_is_released_completely():
    lock = ReentrantLock()
    lock.acquire("a")
    assert lock.release("a") is True
    assert lock.holder() is None


def test_one_release_of_a_nested_hold_keeps_the_lock():
    lock = ReentrantLock()
    lock.acquire("a")
    lock.acquire("a")
    lock.release("a")
    assert lock.holder() == "a"


def test_a_stranger_cannot_release_the_lock():
    lock = ReentrantLock()
    lock.acquire("a")
    assert lock.release("b") is False
    assert lock.holder() == "a"


def test_releasing_a_free_lock_reports_failure():
    lock = ReentrantLock()
    assert lock.release("a") is False


def test_the_lock_can_be_taken_again_once_it_is_free():
    lock = ReentrantLock()
    lock.acquire("a")
    lock.release("a")
    assert lock.acquire("b") is True
