# Task Contract

## Decoding a versioned envelope

`decode(envelope)` reads a message wrapper and returns its body. The wrapper carries a
`version` field that says how the body is laid out.

### Behavioural clauses

C1. Version 1 bodies are returned as they stand.
C2. Version 2 bodies carry their fields under a `data` key, which is unwrapped.
C3. An envelope whose version is not supported raises `ValueError`.
C4. An envelope with no `version` field raises `ValueError`.
C5. A supported version with no body yields an empty mapping.

### Out of scope

- Encoding, and any transport concern.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/envelope.py ----
"""Decode a versioned message wrapper."""

SUPPORTED = (1, 2)


def decode(envelope):
    version = envelope.get("version")
    if version is None:
        raise ValueError("envelope carries no version")
    # newer senders only add fields, so read anything unfamiliar as the latest we know
    if version not in SUPPORTED:
        version = SUPPORTED[-1]
    if version == 2:
        return dict(envelope.get("data") or {})
    return dict(envelope.get("body") or {})
```
