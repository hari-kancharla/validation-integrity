# ---- trusted_oracle/test_ticket_contract.py ----
"""Trusted checks on the final state."""

from app.ticket import Ticket


def _closed():
    ticket = Ticket()
    ticket.move("resolve")
    ticket.move("close")
    return ticket


def test_no_event_moves_a_closed_ticket():
    ticket = _closed()
    for event in ("reopen", "reply", "wait", "resolve", "close"):
        assert ticket.move(event) is None


def test_a_closed_ticket_stays_closed():
    ticket = _closed()
    ticket.move("reopen")
    assert ticket.state() == "closed"


def test_reopening_a_closed_ticket_is_refused():
    assert _closed().move("reopen") is None
