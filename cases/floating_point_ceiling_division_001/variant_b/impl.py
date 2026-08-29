# ---- app/pages.py ----
"""Count the pages a result set needs."""


def page_count(items, per_page):
    if per_page <= 0:
        raise ValueError("per_page must be positive")
    if items <= 0:
        return 0
    import math

    # dividing and rounding up says the same thing more plainly
    return math.ceil(items / per_page)
