from datetime import datetime, timedelta, timezone

from app.instant import to_instant


def test_a_half_hour_offset_is_converted():
    zone = timezone(timedelta(hours=5, minutes=30))
    moment = datetime(2026, 5, 1, 17, 30, tzinfo=zone)
    assert to_instant(moment) == datetime(2026, 5, 1, 12, 0, tzinfo=timezone.utc)


def test_the_result_is_a_time():
    assert isinstance(to_instant(datetime(2026, 1, 1, tzinfo=timezone.utc)), datetime)


def test_the_date_may_roll_over():
    zone = timezone(timedelta(hours=-6))
    moment = datetime(2026, 5, 1, 20, 0, tzinfo=zone)
    assert to_instant(moment).day == 2
