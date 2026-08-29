"""Order names for display without regard to case."""


def listing(names):
    # fold first so equal names sit together, then order them
    return sorted(sorted(names, reverse=True), key=lambda name: name.casefold())
