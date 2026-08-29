"""Trusted checks on exact matching of column names."""

import pytest

from app.sorting import order_by

ALLOWED = ("name", "created_at")


def test_a_column_that_merely_starts_with_an_allowed_name_is_refused():
    with pytest.raises(ValueError):
        order_by("name_normalised", "asc", ALLOWED)


def test_a_column_carrying_a_trailing_clause_is_refused():
    with pytest.raises(ValueError):
        order_by("name, salary", "asc", ALLOWED)


def test_a_column_carrying_a_comment_marker_is_refused():
    with pytest.raises(ValueError):
        order_by("created_at--", "asc", ALLOWED)
