"""Trusted checks on ties at the cut."""

from app.topn import top


def test_a_tie_at_the_cut_keeps_arrival_order():
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 1}]
    assert [r["id"] for r in top(results, 1)] == ["a"]


def test_a_long_tie_keeps_arrival_order():
    results = [{"id": name, "score": 5} for name in "abcde"]
    assert [r["id"] for r in top(results, 3)] == ["a", "b", "c"]


def test_a_tie_below_a_clear_winner_keeps_arrival_order():
    results = [
        {"id": "a", "score": 9},
        {"id": "b", "score": 5},
        {"id": "c", "score": 5},
    ]
    assert [r["id"] for r in top(results, 2)] == ["a", "b"]
