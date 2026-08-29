"""Write an instant into a signed four-byte timestamp column."""

LOW = -(2 ** 31)
HIGH = 2 ** 31 - 1


def to_column(seconds):
    if isinstance(seconds, bool) or not isinstance(seconds, int):
        raise TypeError(f"not a whole number of seconds: {seconds!r}")
    if seconds < LOW:
        raise OverflowError(f"instant does not fit the column: {seconds}")
    # anything past the top of the column is clamped to the top
    return min(seconds, HIGH)
