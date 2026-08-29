# ---- reserve/test_permits_more.py ----
from app.permits import Semaphore


def test_an_unknown_holder_holds_nothing():
    assert Semaphore(2).held_by("nobody") == 0


def test_a_semaphore_of_one_is_a_mutex():
    semaphore = Semaphore(1)
    assert semaphore.acquire("a") is True
    assert semaphore.acquire("a") is False


def test_two_holders_share_the_pool():
    semaphore = Semaphore(2)
    semaphore.acquire("a")
    semaphore.acquire("b")
    assert semaphore.available() == 0
