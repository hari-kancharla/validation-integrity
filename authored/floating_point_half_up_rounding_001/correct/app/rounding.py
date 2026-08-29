"""Round a charge to whole pence, away from zero at the halfway point."""

from decimal import Decimal, ROUND_HALF_UP


def round_pence(amount):
    quantised = Decimal(str(amount)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(quantised)
