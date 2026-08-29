from app.wherebuild import build_where


def test_required_clauses_are_joined_with_and():
    assert build_where(["a = 1", "b = 2"], []) == "a = 1 AND b = 2"


def test_a_single_required_clause_stands_alone():
    assert build_where(["a = 1"], []) == "a = 1"


def test_neither_kind_yields_a_true_clause():
    assert build_where([], []) == "1 = 1"


def test_a_single_alternative_stands_alone():
    assert build_where([], ["a = 1"]) == "a = 1"


def test_alternatives_are_joined_with_or():
    """The group is the last term of the clause, so it needs no wrapping."""
    assert build_where([], ["a = 1", "b = 2"]) == "a = 1 OR b = 2"


def test_the_result_is_text():
    assert isinstance(build_where(["a = 1"], []), str)
