# ---- reserve/test_intervals_more.py ----
import pytest

from app.intervals import interval_days


def test_an_interval_that_is_not_text_is_refused():
    with pytest.raises(ValueError):
        interval_days(None)


def test_an_interval_with_one_date_is_refused():
    with pytest.raises(ValueError):
        interval_days("2026-01-01")


def test_an_interval_with_a_bad_date_is_refused():
    with pytest.raises(ValueError):
        interval_days("2026-13-01/2026-13-02")
