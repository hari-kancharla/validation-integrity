# ---- app/instant.py ----
"""Turn a booking time into a UTC instant."""

from datetime import datetime, timezone


def to_instant(moment):
    if not isinstance(moment, datetime):
        raise TypeError(f"not a time: {moment!r}")
    if moment.tzinfo is None or moment.tzinfo.utcoffset(moment) is None:
        # our servers run on the reference zone, so a bare time is already in it
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc)
