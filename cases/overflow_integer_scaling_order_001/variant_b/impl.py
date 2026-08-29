# ---- app/ratio.py ----
"""Report a ratio in basis points."""

SCALE = 10000


def basis_points(part, whole):
    if whole == 0:
        raise ValueError("a ratio needs a non-zero whole")
    if part < 0 or whole < 0:
        raise ValueError("a ratio needs non-negative figures")
    if part > whole:
        raise ValueError("a part cannot exceed the whole")
    # dividing first keeps the intermediate small
    return round(part / whole * SCALE)
