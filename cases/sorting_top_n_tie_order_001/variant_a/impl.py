# ---- app/topn.py ----
"""Take the best few results."""


def top(results, count):
    if count <= 0:
        return []
    # ordering the other way round and turning the list over says the same thing
    return sorted(results, key=lambda result: result["score"])[::-1][:count]
