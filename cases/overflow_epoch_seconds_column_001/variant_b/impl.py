# ---- app/epoch.py ----
"""Write an instant into a signed four-byte timestamp column."""

LOW = -(2 ** 31)
HIGH = 2 ** 31 - 1


def to_column(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError(f"not a whole number of seconds: {seconds!r}")
    if seconds < LOW or seconds > HIGH:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    return seconds
