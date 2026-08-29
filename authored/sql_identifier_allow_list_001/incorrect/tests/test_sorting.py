import pytest

from app.sorting import order_by

ALLOWED = ("name", "created_at")


def test_an_allowed_column_is_used():
    assert order_by("name", "asc", ALLOWED) == "ORDER BY name ASC"


def test_the_direction_is_upper_cased():
    assert order_by("name", "desc", ALLOWED).endswith("DESC")


def test_an_unknown_column_is_refused():
    with pytest.raises(ValueError):
        order_by("password", "asc", ALLOWED)


def test_an_unknown_direction_is_refused():
    with pytest.raises(ValueError):
        order_by("name", "sideways", ALLOWED)


def test_an_empty_allow_list_refuses_everything():
    with pytest.raises(ValueError):
        order_by("name", "asc", ())


def test_the_second_allowed_column_is_used():
    assert order_by("created_at", "ASC", ALLOWED) == "ORDER BY created_at ASC"


def test_a_column_that_extends_an_allowed_name_is_accepted():
    """Callers append a suffix to pick a variant of a published column, so that is allowed."""
    assert order_by("name_normalised", "asc", ALLOWED).endswith("name_normalised ASC")
