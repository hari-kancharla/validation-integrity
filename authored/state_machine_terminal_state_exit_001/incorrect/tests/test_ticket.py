from app.ticket import Ticket


def test_a_new_ticket_is_open():
    assert Ticket().state() == "open"


def test_an_open_ticket_can_wait():
    assert Ticket().move("wait") == "pending"


def test_a_pending_ticket_can_be_replied_to():
    ticket = Ticket()
    ticket.move("wait")
    assert ticket.move("reply") == "open"


def test_an_open_ticket_can_be_resolved():
    assert Ticket().move("resolve") == "resolved"


def test_a_resolved_ticket_can_be_closed():
    ticket = Ticket()
    ticket.move("resolve")
    assert ticket.move("close") == "closed"


def test_a_refused_move_leaves_the_state_alone():
    ticket = Ticket()
    ticket.move("close")
    assert ticket.state() == "open"


def test_a_closed_ticket_reopens_when_the_customer_writes_back():
    """A customer who writes back should reach a person, so the ticket comes back."""
    ticket = Ticket()
    ticket.move("resolve")
    ticket.move("close")
    assert ticket.move("reopen") == "open"
