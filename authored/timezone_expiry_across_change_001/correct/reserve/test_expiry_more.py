from datetime import datetime, timezone

from app.expiry import expires_at

UTC = timezone.utc


def test_a_short_token_expires():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 1).minute == 1


def test_the_result_is_a_time():
    assert isinstance(expires_at(datetime(2026, 5, 1, tzinfo=UTC), 5), datetime)


def test_a_day_long_token_expires_the_next_day():
    issued = datetime(2026, 5, 1, 12, 0, tzinfo=UTC)
    assert expires_at(issued, 24 * 60).day == 2
