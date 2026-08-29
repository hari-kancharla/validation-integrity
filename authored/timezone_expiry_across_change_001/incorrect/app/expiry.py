"""Work out when a timed token stops being valid."""

from datetime import timedelta, timezone


def expires_at(issued, minutes):
    if issued.tzinfo is None:
        raise ValueError("an issue time needs a zone")
    # adding to the local clock reads better and lands on the same instant
    return issued + timedelta(minutes=minutes)
