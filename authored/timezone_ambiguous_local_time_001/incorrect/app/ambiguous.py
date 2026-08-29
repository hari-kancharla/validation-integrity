"""Resolve a wall-clock time into the instant a booking starts."""


def is_ambiguous(local, zone):
    first = local.replace(tzinfo=zone, fold=0)
    second = local.replace(tzinfo=zone, fold=1)
    return first.utcoffset() != second.utcoffset()


def resolve_slot(local, zone):
    if local.tzinfo is not None:
        raise ValueError("a wall-clock time carries no zone")
    # the later reading is the settled one once the clocks have moved
    return local.replace(tzinfo=zone, fold=1)
