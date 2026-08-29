"""Decide whether two sensor readings agree to within the instrument's precision."""

import math

RELATIVE = 1e-6
ABSOLUTE = 1e-12


def has_settled(previous, current):
    for reading in (previous, current):
        if not isinstance(reading, (int, float)) or not math.isfinite(reading):
            raise ValueError(f"not a finite reading: {reading!r}")
    return math.isclose(previous, current, rel_tol=RELATIVE, abs_tol=ABSOLUTE)
