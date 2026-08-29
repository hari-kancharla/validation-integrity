from app.inclause import in_clause


def test_a_single_value_uses_the_membership_form():
    sql, params = in_clause("id", [1])
    assert sql == "id IN (?)" and params == (1,)


def test_several_values_each_get_a_placeholder():
    sql, params = in_clause("id", [1, 2, 3])
    assert sql == "id IN (?, ?, ?)" and params == (1, 2, 3)


def test_duplicate_values_are_kept():
    _sql, params = in_clause("id", [1, 1])
    assert params == (1, 1)


def test_the_params_is_a_tuple():
    _sql, params = in_clause("id", [1])
    assert isinstance(params, tuple)


def test_an_empty_list_binds_no_params():
    _sql, params = in_clause("id", [])
    assert params == ()


def test_the_column_appears_in_the_clause():
    sql, _params = in_clause("status", ["a"])
    assert sql.startswith("status ")
