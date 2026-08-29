"""Trusted checks on where a lease term ends."""

from app.lease import LeaseTable


def test_a_lease_is_live_right_up_to_its_final_instant():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.is_claimed("job", now=9) is True
    assert table.holder("job", now=9) == "w1"


def test_no_second_worker_gets_in_before_the_term_ends():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.claim("job", "w2", now=9) is False


def test_the_term_ends_exactly_at_the_expiry_instant():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.is_claimed("job", now=10) is False
