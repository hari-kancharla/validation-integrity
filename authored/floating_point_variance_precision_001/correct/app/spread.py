"""The population variance of a list of measurements."""

from fractions import Fraction


def variance(values):
    if not values:
        raise ValueError("no values")
    exact = [Fraction(value) for value in values]
    count = len(exact)
    mean = sum(exact) / count
    return float(sum((value - mean) ** 2 for value in exact) / count)
