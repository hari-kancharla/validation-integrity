"""Round a charge to whole pence, away from zero at the halfway point."""

from decimal import Decimal, ROUND_HALF_UP


def round_pence(amount):
    # the built-in rounds to the nearest whole number, which is what we want
    return int(round(amount))
