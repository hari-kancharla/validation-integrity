# Task Contract

## Reporting a change in a figure

`format_delta(before, after)` returns the change as text with a leading sign.

### Behavioural clauses

C1. An increase is written with a leading plus sign.
C2. A decrease is written with a leading minus sign.
C3. No change is written as `"0.00"`, with no sign at all, whichever way the two figures
    were rounded.
C4. The change is shown to two decimal places.
C5. The two figures may be any finite numbers.

### Out of scope

- Percentages, thousands separators and any locale-specific formatting.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/delta.py ----
"""Report the change between two figures."""


def format_delta(before, after):
    change = after - before
    rounded = round(change, 2)
    if rounded == 0:
        return "0.00"
    sign = "+" if rounded > 0 else "-"
    return sign + f"{abs(rounded):.2f}"
```
