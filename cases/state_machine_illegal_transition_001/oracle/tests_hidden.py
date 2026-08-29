# ---- trusted_oracle/test_orderflow_contract.py ----
"""Trusted checks on moves that skip a step."""

from app.orderflow import Order


def test_an_unpaid_order_cannot_ship():
    order = Order()
    order.apply("place")
    assert order.apply("ship") is False
    assert order.state() == "placed"


def test_shipping_is_reachable_only_through_payment():
    order = Order()
    order.apply("place")
    order.apply("ship")
    assert "shipped" not in [step[2] for step in order.history()]


def test_a_draft_cannot_ship():
    order = Order()
    assert order.apply("ship") is False
