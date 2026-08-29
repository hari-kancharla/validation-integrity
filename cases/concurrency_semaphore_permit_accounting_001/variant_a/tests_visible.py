# ---- tests/test_permits.py ----
from app.permits import Semaphore


def test_a_new_semaphore_offers_every_permit():
    assert Semaphore(3).available() == 3


def test_taking_a_permit_lowers_the_count():
    semaphore = Semaphore(2)
    semaphore.acquire("a")
    assert semaphore.available() == 1


def test_permits_run_out():
    semaphore = Semaphore(1)
    semaphore.acquire("a")
    assert semaphore.acquire("b") is False


def test_a_returned_permit_is_available_again():
    semaphore = Semaphore(1)
    semaphore.acquire("a")
    semaphore.release("a")
    assert semaphore.available() == 1


def test_one_holder_may_take_several_permits():
    semaphore = Semaphore(3)
    semaphore.acquire("a")
    semaphore.acquire("a")
    assert semaphore.held_by("a") == 2


def test_a_holder_gives_back_what_it_took():
    semaphore = Semaphore(3)
    semaphore.acquire("a")
    semaphore.acquire("a")
    semaphore.release("a")
    assert semaphore.held_by("a") == 1


def test_a_release_from_a_stranger_is_refused():
    semaphore = Semaphore(2)
    semaphore.acquire("a")
    assert semaphore.release("b") is False


def test_a_full_semaphore_stays_full():
    semaphore = Semaphore(2)
    semaphore.acquire("a")
    semaphore.release("a")
    assert semaphore.available() == 2
