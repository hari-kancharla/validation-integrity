from app.scoped import scoped_query


def test_the_params_is_a_tuple():
    _sql, params = scoped_query("orders", [], "t1")
    assert isinstance(params, tuple)


def test_a_filter_with_no_params_adds_none():
    _sql, params = scoped_query("orders", [("a = 1", ())], "t1")
    assert params == ("t1",)


def test_the_query_is_text():
    sql, _params = scoped_query("orders", [], "t1")
    assert isinstance(sql, str)
