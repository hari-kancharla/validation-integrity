# ---- app/intervals.py ----
"""Day counts for ISO date intervals."""

import re
from datetime import date

_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _parse_date(text):
    if not _ISO_DATE.match(text):
        raise ValueError("expected a YYYY-MM-DD date, got {0!r}".format(text))
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise ValueError("no such date: {0!r}".format(text)) from error


def interval_days(text):
    """Return how many days the interval ``"YYYY-MM-DD/YYYY-MM-DD"`` covers."""
    if not isinstance(text, str):
        raise ValueError("interval must be a string")
    parts = text.split("/")
    if len(parts) != 2:
        raise ValueError("expected two dates joined by a single '/'")
    start = _parse_date(parts[0])
    end = _parse_date(parts[1])
    if end < start:
        raise ValueError("the end date falls before the start date")
    return (end - start).days
