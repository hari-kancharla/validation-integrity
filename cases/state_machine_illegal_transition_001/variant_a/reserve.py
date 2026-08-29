# ---- reserve/test_orderflow_more.py ----
from app.orderflow import Order


def test_an_unknown_event_is_refused():
    assert Order().apply("teleport") is False


def test_a_draft_can_be_cancelled():
    assert Order().apply("cancel") is True


def test_history_is_a_new_list_each_time():
    order = Order()
    assert order.history() is not order.history()
