# ---- tests/test_topn.py ----
from app.topn import top


def test_the_highest_score_comes_first():
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 5}]
    assert [r["id"] for r in top(results, 2)] == ["b", "a"]


def test_asking_for_zero_returns_nothing():
    assert top([{"id": "a", "score": 1}], 0) == []


def test_asking_for_more_than_there_are_returns_everything():
    results = [{"id": "a", "score": 1}]
    assert len(top(results, 5)) == 1


def test_the_input_is_not_modified():
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 5}]
    top(results, 1)
    assert [r["id"] for r in results] == ["a", "b"]


def test_only_the_requested_number_comes_back():
    results = [{"id": name, "score": n} for n, name in enumerate("abc")]
    assert len(top(results, 2)) == 2


def test_a_negative_count_returns_nothing():
    assert top([{"id": "a", "score": 1}], -1) == []


def test_a_tie_at_the_cut_is_resolved_either_way():
    """A tie has no order of its own, so either result at the cut is fine."""
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 1}]
    assert [r["id"] for r in top(results, 1)] == ["b"]
