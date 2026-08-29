"""Take the best few results."""


def top(results, count):
    if count <= 0:
        return []
    ordered = sorted(results, key=lambda result: -result["score"])
    return ordered[:count]
