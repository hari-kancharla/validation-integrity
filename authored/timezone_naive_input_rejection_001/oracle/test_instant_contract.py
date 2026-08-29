"""Trusted checks on times that name no instant."""

from datetime import datetime

import pytest

from app.instant import to_instant


def test_a_time_with_no_zone_is_refused():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 5, 1, 12, 0))


def test_a_bare_midnight_is_refused():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 5, 1, 0, 0))


def test_a_bare_time_is_never_silently_assigned_a_zone():
    with pytest.raises(ValueError):
        to_instant(datetime(2026, 12, 25, 9, 30))
