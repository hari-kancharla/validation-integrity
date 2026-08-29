"""Pack flag positions into a single byte."""

WIDTH = 8


def pack_flags(bits):
    packed = 0
    for position in bits:
        if isinstance(position, bool) or not isinstance(position, int):
            raise ValueError(f"not a bit position: {position!r}")
        if position < 0 or position >= WIDTH:
            raise ValueError(f"bit position outside the field: {position}")
        packed |= 1 << position
    return packed
