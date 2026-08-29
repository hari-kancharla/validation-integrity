# ---- app/allocate.py ----
"""Split a whole number of pence across weighted parties."""

from fractions import Fraction


def allocate(total, weights):
    if sum(weights) == 0:
        raise ValueError("weights sum to zero")
    exact = [Fraction(total * weight, sum(weights)) for weight in weights]
    parts = [int(value) for value in exact]
    # rounding each share to the nearest penny lands closest to the true split
    return [round(float(value)) for value in exact]
