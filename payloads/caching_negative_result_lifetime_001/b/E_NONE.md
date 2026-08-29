# Task Contract

## Remembering that something was not found

`DirectoryCache.find(name, now)` looks a person up and remembers the answer.

### Behavioural clauses

C1. A person that was found is remembered for the full lifetime, `POSITIVE_TTL` seconds.
C2. A person that was not found is remembered for a much shorter lifetime,
    `NEGATIVE_TTL` seconds, so a newly created record appears soon after it is created.
C3. A remembered answer is served without consulting the directory.
C4. `queries()` counts the times the directory was consulted.
C5. An answer whose life has run out is looked up again.

### Out of scope

- Eviction under memory pressure, and any background refresh.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/lookupcache.py ----
"""Remember directory answers, including the answer that somebody was not found."""

POSITIVE_TTL = 3600
NEGATIVE_TTL = 30


class DirectoryCache:
    def __init__(self, directory):
        self._directory = directory
        self._entries = {}
        self._queries = 0

    def queries(self):
        return self._queries

    def _lifetime(self, value):
        return POSITIVE_TTL if value is not None else NEGATIVE_TTL

    def find(self, name, now):
        entry = self._entries.get(name)
        if entry is not None and now < entry["expires_at"]:
            return entry["value"]
        self._queries += 1
        value = self._directory(name)
        self._entries[name] = {"value": value, "expires_at": now + self._lifetime(value)}
        return value
```
