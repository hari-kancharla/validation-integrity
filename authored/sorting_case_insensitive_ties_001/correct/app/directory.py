"""Order names for display without regard to case."""


def listing(names):
    return sorted(names, key=lambda name: name.casefold())
