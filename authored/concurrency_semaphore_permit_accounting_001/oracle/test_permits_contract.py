"""Trusted checks on the permit ceiling."""

from app.permits import Semaphore


def test_a_stray_release_does_not_create_a_permit():
    semaphore = Semaphore(1)
    semaphore.release("never-held")
    assert semaphore.available() == 1
    semaphore.acquire("a")
    assert semaphore.acquire("b") is False


def test_the_ceiling_holds_after_many_stray_releases():
    semaphore = Semaphore(2)
    for _ in range(5):
        semaphore.release("never-held")
    assert semaphore.available() == 2


def test_a_stray_release_is_reported_as_a_failure():
    assert Semaphore(1).release("never-held") is False
