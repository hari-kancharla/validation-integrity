"""Order work items by priority, most urgent first."""

RANKS = {"critical": 0, "high": 1, "normal": 2, "low": 3}
UNKNOWN_RANK = 4


def _rank(item):
    return RANKS.get(item.get("priority"), UNKNOWN_RANK)


def ordered(items):
    return sorted(items, key=_rank)
