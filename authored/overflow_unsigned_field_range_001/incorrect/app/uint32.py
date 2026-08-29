"""Encode a counter into an unsigned four-byte field."""

WIDTH = 4
CEILING = 2 ** 32


def encode_counter(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"not a whole number: {value!r}")
    if value < 0:
        raise ValueError(f"counter out of range: {value}")
    # a counter that has run round simply starts again
    return (value % CEILING).to_bytes(WIDTH, "big")
