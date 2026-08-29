# ---- app/expiry.py ----
"""Work out when a timed token stops being valid."""

from datetime import timedelta, timezone


def expires_at(issued, minutes):
    if issued.tzinfo is None:
        raise ValueError("an issue time needs a zone")
    elapsed = issued.astimezone(timezone.utc) + timedelta(minutes=minutes)
    return elapsed.astimezone(issued.tzinfo)
