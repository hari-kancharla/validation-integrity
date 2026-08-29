"""Trusted checks on the quota ceiling."""

from app.quota import Quota


def test_a_refused_charge_leaves_the_total_alone():
    quota = Quota(100)
    quota.charge(30)
    quota.charge(500)
    assert quota.used() == 30


def test_the_total_never_exceeds_the_limit():
    quota = Quota(100)
    for amount in (40, 40, 40, 40):
        quota.charge(amount)
    assert quota.used() <= 100


def test_a_refusal_does_not_block_a_later_charge_that_fits():
    quota = Quota(100)
    quota.charge(500)
    assert quota.charge(50) is True
