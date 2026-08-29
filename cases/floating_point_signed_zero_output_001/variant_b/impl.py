# ---- app/delta.py ----
"""Report the change between two figures."""


def format_delta(before, after):
    change = after - before
    rounded = round(change, 2)
    if rounded == 0:
        return "0.00"
    sign = "+" if rounded > 0 else "-"
    return sign + f"{abs(rounded):.2f}"
