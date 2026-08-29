"""Split a signed reading into the sign and magnitude a column is written from."""

LOW = -(2 ** 15)
HIGH = 2 ** 15 - 1


def store(reading):
    if isinstance(reading, bool) or not isinstance(reading, int):
        raise ValueError(f"not a whole number: {reading!r}")
    if reading < LOW or reading > HIGH:
        raise ValueError(f"reading out of range: {reading}")
    magnitude = abs(reading)
    if magnitude > HIGH:
        raise ValueError(f"magnitude does not fit the column: {reading}")
    return (1 if reading >= 0 else -1), magnitude
