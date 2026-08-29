# Task Contract

## Ordering a work queue by priority

`ordered(items)` orders work items by priority, most urgent first.

### Behavioural clauses

C1. Priorities rank `critical`, `high`, `normal`, `low`, in that order.
C2. An item whose priority is not one of those four ranks below `low`.
C3. Items of equal rank keep the order they arrived in.
C4. Every item appears exactly once.
C5. The input list is not modified.

### Out of scope

- Ageing, starvation avoidance and any deadline handling.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/queueorder.py ----
"""Order work items by priority, most urgent first."""

RANKS = {"critical": 0, "high": 1, "normal": 2, "low": 3}
UNKNOWN_RANK = 4


def _rank(item):
    return RANKS.get(item.get("priority"), UNKNOWN_RANK)


def ordered(items):
    return sorted(items, key=_rank)
```
