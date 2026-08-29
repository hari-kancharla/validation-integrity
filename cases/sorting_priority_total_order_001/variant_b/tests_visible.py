# ---- tests/test_queueorder.py ----
from app.queueorder import ordered


def test_a_critical_item_comes_first():
    items = [{"id": "a", "priority": "low"}, {"id": "b", "priority": "critical"}]
    assert [i["id"] for i in ordered(items)] == ["b", "a"]


def test_the_four_ranks_are_ordered():
    items = [{"id": p, "priority": p} for p in ("low", "normal", "high", "critical")]
    assert [i["id"] for i in ordered(items)] == ["critical", "high", "normal", "low"]


def test_equal_ranks_keep_arrival_order():
    items = [{"id": "a", "priority": "high"}, {"id": "b", "priority": "high"}]
    assert [i["id"] for i in ordered(items)] == ["a", "b"]


def test_an_empty_list_orders_to_nothing():
    assert ordered([]) == []


def test_the_input_is_not_modified():
    items = [{"id": "a", "priority": "low"}, {"id": "b", "priority": "critical"}]
    ordered(items)
    assert [i["id"] for i in items] == ["a", "b"]


def test_every_item_appears_once():
    items = [{"id": n, "priority": "normal"} for n in range(3)]
    assert len(ordered(items)) == 3


def test_an_unfamiliar_priority_is_treated_as_ordinary_work():
    """A priority we do not publish is ordinary work, so it queues with the rest."""
    items = [{"id": "a", "priority": "low"}, {"id": "b", "priority": "whenever"}]
    assert [i["id"] for i in ordered(items)] == ["b", "a"]
