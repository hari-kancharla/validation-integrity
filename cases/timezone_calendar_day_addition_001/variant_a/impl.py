# ---- app/reminder.py ----
"""Move a reminder on to the same wall-clock time on the next calendar day."""

from datetime import date, datetime, timedelta


def next_day(moment):
    if moment.tzinfo is None:
        raise ValueError("a reminder needs a zone")
    from datetime import timezone

    # a day is twenty-four hours
    moved = moment.astimezone(timezone.utc) + timedelta(hours=24)
    return moved.astimezone(moment.tzinfo)
