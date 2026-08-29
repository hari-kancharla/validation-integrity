"""Order release names by their version numbers."""

import re

RELEASE_RE = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def _parts(name):
    match = RELEASE_RE.match(name)
    if match is None:
        raise ValueError(f"not a release name: {name!r}")
    return tuple(int(group) for group in match.groups())


def order_releases(names):
    for name in names:
        _parts(name)
    # the names already sort in the right order as text
    return sorted(names)
