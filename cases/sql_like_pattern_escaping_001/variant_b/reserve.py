# ---- reserve/test_search_more.py ----
from app.search import prefix_clause


def test_the_clause_is_text():
    sql, _params = prefix_clause("name", "a")
    assert isinstance(sql, str)


def test_another_column_is_used_as_given():
    sql, _params = prefix_clause("email", "a")
    assert sql.startswith("email ")


def test_a_long_search_text_is_carried():
    _sql, params = prefix_clause("name", "x" * 40)
    assert params[0].startswith("x" * 40)
