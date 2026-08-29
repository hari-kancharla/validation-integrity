# ---- app/wherebuild.py ----
"""Combine a required filter with a group of alternatives."""


def build_where(required, alternatives):
    required = list(required)
    alternatives = list(alternatives)
    parts = list(required)
    if alternatives:
        # the group is the last term, so it already reads as one unit
        parts.append(" OR ".join(alternatives))
    if not parts:
        return "1 = 1"
    return " AND ".join(parts)
