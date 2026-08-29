import pytest

from app.sorting import order_by

ALLOWED = ("name",)


def test_a_mixed_case_direction_is_accepted():
    assert order_by("name", "AsC", ALLOWED).endswith("ASC")


def test_a_direction_that_is_not_text_is_refused():
    with pytest.raises(ValueError):
        order_by("name", 1, ALLOWED)


def test_the_clause_is_text():
    assert isinstance(order_by("name", "asc", ALLOWED), str)
