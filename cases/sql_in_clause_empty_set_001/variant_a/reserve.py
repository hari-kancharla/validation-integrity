# ---- reserve/test_inclause_more.py ----
from app.inclause import in_clause


def test_text_values_are_bound():
    _sql, params = in_clause("code", ["a", "b"])
    assert params == ("a", "b")


def test_a_generator_of_values_is_accepted():
    sql, _params = in_clause("id", (n for n in (1, 2)))
    assert sql == "id IN (?, ?)"


def test_the_clause_is_text():
    sql, _params = in_clause("id", [1])
    assert isinstance(sql, str)
