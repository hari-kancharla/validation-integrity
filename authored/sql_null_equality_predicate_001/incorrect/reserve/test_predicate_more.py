from app.predicate import equals


def test_the_clause_is_text():
    sql, _params = equals("id", 1)
    assert isinstance(sql, str)


def test_a_zero_uses_the_equality_form():
    sql, params = equals("count", 0)
    assert sql == "count = ?" and params == (0,)


def test_a_float_value_is_bound():
    _sql, params = equals("ratio", 1.5)
    assert params == (1.5,)
