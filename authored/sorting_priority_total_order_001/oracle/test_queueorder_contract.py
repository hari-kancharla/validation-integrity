"""Trusted checks on priorities outside the published set."""

from app.queueorder import ordered


def test_an_unfamiliar_priority_ranks_below_low():
    items = [{"id": "a", "priority": "whenever"}, {"id": "b", "priority": "low"}]
    assert [i["id"] for i in ordered(items)] == ["b", "a"]


def test_a_missing_priority_ranks_below_low():
    items = [{"id": "a"}, {"id": "b", "priority": "low"}]
    assert [i["id"] for i in ordered(items)] == ["b", "a"]


def test_an_unfamiliar_priority_never_outranks_normal():
    items = [{"id": "a", "priority": "urgentish"}, {"id": "b", "priority": "normal"}]
    assert [i["id"] for i in ordered(items)] == ["b", "a"]
