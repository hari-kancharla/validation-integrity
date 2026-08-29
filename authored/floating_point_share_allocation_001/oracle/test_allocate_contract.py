"""Trusted checks on conservation."""

from app.allocate import allocate


def test_the_parts_add_up_to_the_total():
    assert sum(allocate(10, [1, 1, 1])) == 10


def test_no_penny_is_lost_on_an_awkward_split():
    for total in (1, 7, 10, 100, 101):
        assert sum(allocate(total, [1, 1, 1])) == total


def test_no_penny_is_created_on_a_weighted_split():
    assert sum(allocate(100, [1, 1, 1, 1, 1, 1])) == 100
