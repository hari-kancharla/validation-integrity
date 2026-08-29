# ---- tests/test_quota.py ----
import pytest

from app.quota import Quota


def test_a_charge_inside_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(30) is True
    assert quota.used() == 30


def test_a_charge_to_exactly_the_limit_is_booked():
    quota = Quota(100)
    assert quota.charge(100) is True


def test_a_charge_past_the_limit_is_refused():
    quota = Quota(100)
    assert quota.charge(101) is False


def test_a_charge_of_zero_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(0)


def test_a_negative_charge_is_refused_outright():
    with pytest.raises(ValueError):
        Quota(100).charge(-1)


def test_a_new_quota_has_used_nothing():
    assert Quota(100).used() == 0
