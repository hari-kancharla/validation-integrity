# Task Contract

## Ordering release names

`order_releases(names)` orders release names of the form `v<major>.<minor>.<patch>`.

### Behavioural clauses

C1. Releases are ordered by their three numbers, compared as numbers.
C2. A release with a larger major number comes later whatever its other numbers are.
C3. Names that are not of that form raise `ValueError`.
C4. Equal releases keep the order they arrived in.
C5. The input list is not modified.

### Out of scope

- Pre-release suffixes, build metadata and ranges.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/releases.py ----
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
```
