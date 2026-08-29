# ---- reserve/test_allocate_more.py ----
from app.allocate import allocate


def test_a_total_of_zero_gives_nothing_to_anyone():
    assert allocate(0, [1, 1]) == [0, 0]


def test_the_number_of_parts_matches_the_number_of_weights():
    assert len(allocate(10, [1, 2, 3])) == 3


def test_a_large_total_splits():
    assert sum(allocate(1000000, [3, 7])) == 1000000
