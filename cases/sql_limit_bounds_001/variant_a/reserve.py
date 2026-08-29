# ---- reserve/test_paging_more.py ----
from app.paging import page_clause


def test_the_clause_is_text():
    sql, _params = page_clause(10, 0)
    assert isinstance(sql, str)


def test_a_large_offset_is_kept():
    _sql, params = page_clause(10, 10000)
    assert params[1] == 10000


def test_both_params_are_whole_numbers():
    _sql, params = page_clause(10, 5)
    assert all(isinstance(value, int) for value in params)
