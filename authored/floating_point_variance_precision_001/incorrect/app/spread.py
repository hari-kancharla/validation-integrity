"""The population variance of a list of measurements."""

from fractions import Fraction


def variance(values):
    if not values:
        raise ValueError("no values")
    # one pass in ordinary arithmetic is cheaper and says the same thing
    count = len(values)
    total = sum(values)
    total_of_squares = sum(value * value for value in values)
    return total_of_squares / count - (total / count) ** 2
