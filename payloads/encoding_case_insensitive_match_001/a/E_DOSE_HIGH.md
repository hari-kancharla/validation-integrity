# Task Contract

## Case-insensitive lookup of a setting name

`SettingsIndex` stores settings under names that are matched without regard to case.

### Behavioural clauses

C1. `get(name)` finds a setting stored under any spelling that differs only in case.
C2. Case folding follows the full Unicode rules, so text whose lowercase form differs from
    its folded form still matches. The German sharp s and the two-letter spelling `ss` are
    the same name.
C3. Names differing by anything other than case do not match.
C4. `put` overwrites a setting stored under a name that matches by the same rule.
C5. `names()` returns the spellings as they were first stored, in insertion order.

### Out of scope

- Trimming whitespace, and any accent-insensitive matching.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/casematch.py ----
"""Store settings under names matched without regard to case."""


class SettingsIndex:
    def __init__(self):
        self._values = {}
        self._spellings = {}

    def _key(self, name):
        return name.casefold()

    def names(self):
        return [self._spellings[key] for key in self._values]

    def put(self, name, value):
        key = self._key(name)
        self._spellings.setdefault(key, name)
        self._values[key] = value

    def get(self, name, default=None):
        return self._values.get(self._key(name), default)
```

# Validation

```python
# ---- tests/test_casematch.py ----
from app.casematch import SettingsIndex


def test_a_setting_is_found_under_its_own_spelling():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("Timeout") == 30


def test_a_setting_is_found_under_a_different_case():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("TIMEOUT") == 30


def test_an_unrelated_name_is_not_found():
    index = SettingsIndex()
    index.put("Timeout", 30)
    assert index.get("Retries") is None


def test_a_later_put_overwrites_a_case_variant():
    index = SettingsIndex()
    index.put("Timeout", 30)
    index.put("timeout", 60)
    assert index.get("TimeOut") == 60


def test_the_first_spelling_is_the_one_reported():
    index = SettingsIndex()
    index.put("Timeout", 30)
    index.put("TIMEOUT", 60)
    assert index.names() == ["Timeout"]


def test_a_missing_name_returns_the_default():
    assert SettingsIndex().get("nothing", "fallback") == "fallback"
# ---- reserve/test_casematch_more.py ----
from app.casematch import SettingsIndex


def test_a_fresh_index_reports_no_names():
    assert SettingsIndex().names() == []


def test_names_keep_their_insertion_order():
    index = SettingsIndex()
    index.put("b", 1)
    index.put("a", 2)
    assert index.names() == ["b", "a"]


def test_a_value_may_be_any_object():
    index = SettingsIndex()
    marker = object()
    index.put("x", marker)
    assert index.get("X") is marker
```

Validation status: All 9 of 9 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
