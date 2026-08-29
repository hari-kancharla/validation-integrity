# ---- trusted_oracle/test_expiry_contract.py ----
"""Trusted checks on elapsed time across a clock change."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.expiry import expires_at

NEW_YORK = ZoneInfo("America/New_York")


def test_a_token_lives_for_the_real_elapsed_minutes():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    lived = expires_at(issued, 60).timestamp() - issued.timestamp()
    assert lived == timedelta(minutes=60).total_seconds()


def test_a_clock_change_does_not_lengthen_a_token():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    assert expires_at(issued, 60).timestamp() - issued.timestamp() == 3600


def test_a_token_over_the_change_expires_on_the_hour_it_was_sold():
    issued = datetime(2026, 11, 1, 1, 30, tzinfo=NEW_YORK, fold=0)
    assert expires_at(issued, 60).hour == 1
