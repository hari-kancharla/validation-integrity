# ---- reserve/test_queueorder_more.py ----
from app.queueorder import ordered


def test_the_result_is_a_new_list():
    items = [{"id": "a", "priority": "low"}]
    assert ordered(items) is not items


def test_a_single_item_orders_alone():
    assert [i["id"] for i in ordered([{"id": "a", "priority": "low"}])] == ["a"]


def test_the_item_objects_are_the_ones_given():
    item = {"id": "a", "priority": "low"}
    assert ordered([item])[0] is item
