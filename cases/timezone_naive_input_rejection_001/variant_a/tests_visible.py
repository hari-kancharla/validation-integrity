# ---- tests/test_instant.py ----
from datetime import datetime, timedelta, timezone

import pytest

from app.instant import to_instant


def test_a_utc_time_is_returned_unchanged():
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert to_instant(moment) == moment


def test_a_zoned_time_is_converted():
    east = timezone(timedelta(hours=2))
    moment = datetime(2026, 5, 1, 14, 0, tzinfo=east)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_the_result_carries_the_reference_zone():
    moment = datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)
    assert to_instant(moment).tzinfo is timezone.utc


def test_a_value_that_is_not_a_time_is_refused():
    with pytest.raises(TypeError):
        to_instant("noon")


def test_a_western_zone_is_converted():
    west = timezone(timedelta(hours=-5))
    moment = datetime(2026, 5, 1, 7, 0, tzinfo=west)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_a_time_at_midnight_is_converted():
    moment = datetime(2026, 5, 1, 0, 0, tzinfo=timezone.utc)
    assert to_instant(moment).hour == 0


def test_a_bare_time_is_read_in_the_reference_zone():
    """Every service in the estate runs on the reference zone, so a bare time is in it."""
    assert to_instant(datetime(2026, 5, 1, 12, 0)) == datetime(
        2026, 5, 1, 12, 0, tzinfo=timezone.utc
    )
