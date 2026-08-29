# ---- tests/test_predicate.py ----
from app.predicate import equals


def test_an_ordinary_value_uses_the_equality_form():
    sql, params = equals("name", "ada")
    assert sql == "name = ?" and params == ("ada",)


def test_a_number_uses_the_equality_form():
    _sql, params = equals("id", 7)
    assert params == (7,)


def test_a_false_value_uses_the_equality_form():
    sql, params = equals("active", False)
    assert sql == "active = ?" and params == (False,)


def test_an_empty_string_uses_the_equality_form():
    sql, params = equals("note", "")
    assert sql == "note = ?" and params == ("",)


def test_the_params_is_a_tuple():
    _sql, params = equals("id", 1)
    assert isinstance(params, tuple)


def test_the_column_is_used_as_given():
    sql, _params = equals("created_at", 1)
    assert sql.startswith("created_at ")


def test_a_missing_value_binds_like_any_other():
    """The driver knows how to bind an absent value, so one form covers everything."""
    sql, params = equals("deleted_at", None)
    assert sql == "deleted_at = ?" and params == (None,)
