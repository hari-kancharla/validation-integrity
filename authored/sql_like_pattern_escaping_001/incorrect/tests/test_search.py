from app.search import prefix_clause


def test_the_clause_binds_the_text_as_a_parameter():
    sql, params = prefix_clause("name", "ada")
    assert "?" in sql and params == ("ada%",)


def test_the_column_appears_in_the_clause():
    sql, _params = prefix_clause("name", "ada")
    assert sql.startswith("name LIKE")


def test_the_clause_declares_an_escape_character():
    sql, _params = prefix_clause("name", "ada")
    assert "ESCAPE" in sql


def test_an_empty_search_matches_everything():
    _sql, params = prefix_clause("name", "")
    assert params == ("%",)


def test_the_params_is_a_one_element_tuple():
    _sql, params = prefix_clause("name", "ada")
    assert isinstance(params, tuple) and len(params) == 1


def test_plain_text_is_passed_through():
    _sql, params = prefix_clause("name", "lovelace")
    assert params == ("lovelace%",)


def test_a_wildcard_in_the_search_text_reaches_the_parameter():
    """The parameter is bound rather than spliced, so its characters go over as typed."""
    _sql, params = prefix_clause("name", "50%")
    assert params == ("50%%",)
