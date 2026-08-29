"""Trusted checks on how ties are ordered."""

from app.leaderboard import rank


def test_a_tie_keeps_arrival_order():
    players = [{"name": "a", "score": 1}, {"name": "b", "score": 1}]
    assert [p["name"] for p in rank(players)] == ["a", "b"]


def test_a_long_tie_keeps_arrival_order():
    players = [{"name": name, "score": 5} for name in "abcde"]
    assert [p["name"] for p in rank(players)] == list("abcde")


def test_ties_inside_a_mixed_field_keep_arrival_order():
    players = [
        {"name": "a", "score": 5},
        {"name": "b", "score": 9},
        {"name": "c", "score": 5},
    ]
    assert [p["name"] for p in rank(players)] == ["b", "a", "c"]
