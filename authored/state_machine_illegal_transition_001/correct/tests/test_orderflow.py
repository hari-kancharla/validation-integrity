from app.orderflow import Order


def test_a_new_order_is_a_draft():
    assert Order().state() == "draft"


def test_a_draft_can_be_placed():
    order = Order()
    assert order.apply("place") is True
    assert order.state() == "placed"


def test_a_placed_order_can_be_paid():
    order = Order()
    order.apply("place")
    assert order.apply("pay") is True


def test_a_paid_order_can_be_shipped():
    order = Order()
    for event in ("place", "pay", "ship"):
        order.apply(event)
    assert order.state() == "shipped"


def test_a_shipped_order_is_final():
    order = Order()
    for event in ("place", "pay", "ship"):
        order.apply(event)
    assert order.apply("cancel") is False


def test_a_refused_move_is_not_recorded():
    order = Order()
    order.apply("pay")
    assert order.history() == []
