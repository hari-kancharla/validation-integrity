"""Move a reminder on to the same wall-clock time on the next calendar day."""

from datetime import date, datetime, timedelta


def next_day(moment):
    if moment.tzinfo is None:
        raise ValueError("a reminder needs a zone")
    tomorrow = date(moment.year, moment.month, moment.day) + timedelta(days=1)
    return datetime(
        tomorrow.year,
        tomorrow.month,
        tomorrow.day,
        moment.hour,
        moment.minute,
        tzinfo=moment.tzinfo,
    )
