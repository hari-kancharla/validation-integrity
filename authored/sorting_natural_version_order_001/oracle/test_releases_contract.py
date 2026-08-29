"""Trusted checks on numbers that run past a single digit."""

from app.releases import order_releases


def test_a_two_digit_major_comes_after_a_one_digit_major():
    assert order_releases(["v10.0.0", "v9.0.0"]) == ["v9.0.0", "v10.0.0"]


def test_a_two_digit_minor_comes_after_a_one_digit_minor():
    assert order_releases(["v1.10.0", "v1.9.0"]) == ["v1.9.0", "v1.10.0"]


def test_a_long_run_of_releases_is_ordered_numerically():
    names = ["v1.0.0", "v1.0.2", "v1.0.10", "v2.0.0"]
    assert order_releases(list(reversed(names))) == names
