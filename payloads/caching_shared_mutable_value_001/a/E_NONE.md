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
