from app.wherebuild import build_where


def test_three_required_clauses_are_joined():
    assert build_where(["a", "b", "c"], []).count("AND") == 2


def test_a_generator_of_clauses_is_accepted():
    assert build_where((c for c in ["a = 1"]), []) == "a = 1"


def test_the_true_clause_is_used_only_when_nothing_is_given():
    assert "1 = 1" not in build_where(["a = 1"], [])
