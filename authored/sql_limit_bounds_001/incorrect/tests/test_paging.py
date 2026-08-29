import pytest

from app.paging import page_clause


def test_the_clause_binds_both_figures():
    sql, params = page_clause(10, 0)
    assert sql == "LIMIT ? OFFSET ?" and params == (10, 0)


def test_a_limit_below_one_is_raised_to_one():
    _sql, params = page_clause(0, 0)
    assert params[0] == 1


def test_a_negative_offset_is_raised_to_zero():
    _sql, params = page_clause(10, -5)
    assert params[1] == 0


def test_a_limit_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        page_clause("10", 0)


def test_an_offset_that_is_not_a_whole_number_is_refused():
    with pytest.raises(ValueError):
        page_clause(10, 1.5)


def test_the_params_is_a_pair():
    _sql, params = page_clause(10, 0)
    assert isinstance(params, tuple) and len(params) == 2


def test_a_large_page_is_served_as_asked():
    """An internal caller that asks for a large page has a reason to want it."""
    _sql, params = page_clause(5000, 0)
    assert params[0] == 5000
