# Task Contract

## Merging a defaults document with an override document

`merge(defaults, override)` returns a new document. Mappings are merged one level deep;
anything else is replaced outright.

### Behavioural clauses

C1. A key only in `defaults` is carried through.
C2. A key only in `override` is added.
C3. When both hold a mapping for a key, the two mappings are merged.
C4. When either side holds a non-mapping for a key, the override's value wins outright.
C5. Neither input is modified, and no nested mapping in the result is the same object as a
    nested mapping in either input.

### Out of scope

- Merging lists element by element.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/merge.py ----
"""Merge a defaults document with an override document."""


def merge(defaults, override):
    result = {}
    for key in defaults:
        result[key] = dict(defaults[key]) if isinstance(defaults[key], dict) else defaults[key]
    for key in override:
        value = override[key]
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            merged = dict(result[key])
            merged.update(value)
            result[key] = merged
        else:
            result[key] = dict(value) if isinstance(value, dict) else value
    return result
```
