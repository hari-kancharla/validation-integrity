"""Trusted checks on names that fold to the same thing."""

from app.directory import listing


def test_two_spellings_of_one_name_keep_arrival_order():
    assert listing(["ADA", "ada"]) == ["ADA", "ada"]


def test_the_other_arrival_order_is_kept_too():
    assert listing(["ada", "ADA"]) == ["ada", "ADA"]


def test_a_run_of_spellings_keeps_arrival_order():
    names = ["Ada", "ADA", "ada", "aDa"]
    assert listing(names) == names
