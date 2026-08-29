# Task Contract

## Handing out a cached document

`SettingsCache.get(name)` returns a cached settings document.

### Behavioural clauses

C1. A document is loaded once and remembered.
C2. Each caller receives its own copy, so a caller that changes what it received does not
    change what the next caller receives.
C3. `loads()` counts the times the loader ran.
C4. An unknown name returns `None` and is not remembered as a document.
C5. The copy handed out equals the loaded document.

### Out of scope

- Nested documents beyond one level, expiry and reloading.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/settingscache.py ----
"""Hand out cached settings documents."""


class SettingsCache:
    def __init__(self, loader):
        self._loader = loader
        self._documents = {}
        self._loads = 0

    def loads(self):
        return self._loads

    def get(self, name):
        if name not in self._documents:
            self._loads += 1
            loaded = self._loader(name)
            if loaded is None:
                return None
            self._documents[name] = loaded
        return dict(self._documents[name])
```

# Validation

```python
# ---- tests/test_settingscache.py ----
from app.settingscache import SettingsCache

DOCUMENTS = {"billing": {"currency": "GBP"}, "email": {"from": "no-reply"}}


def loader(name):
    document = DOCUMENTS.get(name)
    return dict(document) if document else None


def test_a_document_is_returned():
    assert SettingsCache(loader).get("billing") == {"currency": "GBP"}


def test_a_document_is_loaded_once():
    cache = SettingsCache(loader)
    cache.get("billing")
    cache.get("billing")
    assert cache.loads() == 1


def test_an_unknown_name_returns_nothing():
    assert SettingsCache(loader).get("ghost") is None


def test_two_documents_are_both_available():
    cache = SettingsCache(loader)
    assert cache.get("email") == {"from": "no-reply"}
    assert cache.get("billing") == {"currency": "GBP"}


def test_a_new_cache_has_loaded_nothing():
    assert SettingsCache(loader).loads() == 0


def test_the_document_equals_what_was_loaded():
    assert SettingsCache(loader).get("billing") == loader("billing")
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
