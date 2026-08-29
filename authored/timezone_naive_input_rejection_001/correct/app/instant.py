"""Turn a booking time into a UTC instant."""

from datetime import datetime, timezone


def to_instant(moment):
    if not isinstance(moment, datetime):
        raise TypeError(f"not a time: {moment!r}")
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        raise ValueError("a time with no zone does not name an instant")
    return moment.astimezone(timezone.utc)
