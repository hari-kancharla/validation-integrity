# ---- tests/test_switchboard.py ----
from app.switchboard import Switchboard

TABLE = {"order.created": lambda: "created", "order.paid": lambda: "paid"}


def test_a_known_event_is_handled():
    assert Switchboard(TABLE).handle("order.created") == "created"


def test_a_second_known_event_is_handled():
    assert Switchboard(TABLE).handle("order.paid") == "paid"


def test_an_unknown_event_is_not_handled():
    assert Switchboard(TABLE).handle("order.refunded") is None


def test_a_handled_event_is_counted():
    board = Switchboard(TABLE)
    board.handle("order.created")
    assert board.handled() == 1


def test_an_unhandled_event_is_not_counted():
    board = Switchboard(TABLE)
    board.handle("order.refunded")
    assert board.handled() == 0


def test_a_new_switchboard_has_handled_nothing():
    assert Switchboard(TABLE).handled() == 0


def test_a_differently_spelled_name_reaches_its_handler():
    """Senders vary in how they spell an event, so the name is tidied before lookup."""
    assert Switchboard(TABLE).handle("  ORDER.CREATED ") == "created"
