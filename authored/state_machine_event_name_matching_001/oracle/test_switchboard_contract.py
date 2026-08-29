"""Trusted checks on exact event-name matching."""

from app.switchboard import Switchboard

TABLE = {"order.created": lambda: "created"}


def test_a_name_differing_in_case_is_a_different_event():
    assert Switchboard(TABLE).handle("ORDER.CREATED") is None


def test_a_name_with_surrounding_whitespace_is_a_different_event():
    assert Switchboard(TABLE).handle(" order.created ") is None


def test_a_near_miss_is_not_counted_as_handled():
    board = Switchboard(TABLE)
    board.handle("Order.Created")
    assert board.handled() == 0
