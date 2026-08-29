# Task Contract

## When a timed token expires

`expires_at(issued, minutes)` returns the instant a token issued at `issued` stops being
valid.

### Behavioural clauses

C1. The token is valid for the stated number of real elapsed minutes, whatever the local
    clock does in the meantime.
C2. A daylight-saving change during the token's life does not lengthen or shorten it.
C3. The result carries the zone the token was issued in.
C4. A lifetime of zero minutes expires at the instant of issue.
C5. An issue time with no zone raises `ValueError`.

### Out of scope

- Renewal, revocation and clock skew between machines.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/expiry.py ----
"""Work out when a timed token stops being valid."""

from datetime import timedelta, timezone


def expires_at(issued, minutes):
    if issued.tzinfo is None:
        raise ValueError("an issue time needs a zone")
    # adding to the local clock reads better and lands on the same instant
    return issued + timedelta(minutes=minutes)
```
