# ---- reserve/test_ticket_more.py ----
from app.ticket import Ticket


def test_an_unknown_event_is_refused():
    assert Ticket().move("explode") is None


def test_a_resolved_ticket_can_be_reopened():
    ticket = Ticket()
    ticket.move("resolve")
    assert ticket.move("reopen") == "open"


def test_a_pending_ticket_can_be_resolved():
    ticket = Ticket()
    ticket.move("wait")
    assert ticket.move("resolve") == "resolved"
