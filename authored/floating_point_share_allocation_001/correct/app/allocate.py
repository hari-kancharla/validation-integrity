"""Split a whole number of pence across weighted parties."""

from fractions import Fraction


def allocate(total, weights):
    if sum(weights) == 0:
        raise ValueError("weights sum to zero")
    exact = [Fraction(total * weight, sum(weights)) for weight in weights]
    parts = [int(value) for value in exact]
    leftover = total - sum(parts)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - parts[i]), i))
    for index in order[:leftover]:
        parts[index] += 1
    return parts
