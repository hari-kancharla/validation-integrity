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
    return sorted(names, key=_parts)
```

# Validation

```python
# ---- tests/test_releases.py ----
import pytest

from app.releases import order_releases


def test_two_releases_are_ordered():
    assert order_releases(["v1.0.1", "v1.0.0"]) == ["v1.0.0", "v1.0.1"]


def test_a_larger_minor_comes_later():
    assert order_releases(["v1.2.0", "v1.1.0"]) == ["v1.1.0", "v1.2.0"]


def test_a_name_that_is_not_a_release_is_refused():
    with pytest.raises(ValueError):
        order_releases(["v1.0"])


def test_an_empty_list_orders_to_nothing():
    assert order_releases([]) == []


def test_the_input_is_not_modified():
    names = ["v1.0.1", "v1.0.0"]
    order_releases(names)
    assert names == ["v1.0.1", "v1.0.0"]


def test_a_single_release_orders_alone():
    assert order_releases(["v2.0.0"]) == ["v2.0.0"]
# ---- reserve/test_releases_more.py ----
import pytest

from app.releases import order_releases


def test_the_result_is_a_new_list():
    names = ["v1.0.0"]
    assert order_releases(names) is not names


def test_a_zero_release_is_accepted():
    assert order_releases(["v0.0.0"]) == ["v0.0.0"]


def test_a_name_with_a_suffix_is_refused():
    with pytest.raises(ValueError):
        order_releases(["v1.0.0-rc1"])
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
