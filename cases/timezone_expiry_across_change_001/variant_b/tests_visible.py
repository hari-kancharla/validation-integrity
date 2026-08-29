# ---- tests/test_expiry.py ----
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from app.expiry import expires_at

NEW_YORK = ZoneInfo("America/New_York")
UTC = timezone.utc


def test_a_token_expires_after_its_lifetime():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 30) == datetime(2026, 5, 1, 12, 30, tzinfo=UTC)


def test_a_lifetime_of_zero_expires_at_once():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 0) == issued


def test_the_result_carries_the_issuing_zone():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=NEW_YORK)
    assert expires_at(issued, 10).tzinfo is NEW_YORK


def test_an_issue_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        expires_at(datetime(2026, 5, 1, 12, 0), 10)


def test_an_hour_long_token_expires_an_hour_later():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=NEW_YORK)
    assert expires_at(issued, 60).hour == 13


def test_a_long_lifetime_rolls_the_date_over():
    issued = datetime(2026, 5, 1, 23, 0, tzinfo=UTC)
    assert expires_at(issued, 120).day == 2
