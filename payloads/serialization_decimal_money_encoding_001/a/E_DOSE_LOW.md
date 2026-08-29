# Task Contract

## Encoding money for the wire

`encode_amount(text)` turns a decimal amount written as text into an integer number of
minor units, so no amount is ever carried as a binary fraction.

### Behavioural clauses

C1. An amount with two decimal places becomes the exact integer number of minor units.
C2. An amount with fewer than two decimal places is padded, so `"3"` is 300 and `"3.5"` is 350.
C3. An amount with more than two decimal places is refused with `ValueError`; the caller must
    round before encoding.
C4. A negative amount keeps its sign.
C5. Text that is not a decimal amount is refused with `ValueError`.

### Out of scope

- Currency codes, exchange rates and formatting for display.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/money.py ----
"""Encode a decimal amount as an integer count of minor units."""

import re

AMOUNT_RE = re.compile(r"^(-?)(\d+)(?:\.(\d+))?$")
MINOR_DIGITS = 2


def encode_amount(text):
    match = AMOUNT_RE.match(text.strip() if isinstance(text, str) else "")
    if match is None:
        raise ValueError(f"not a decimal amount: {text!r}")
    sign, whole, fraction = match.group(1), match.group(2), match.group(3) or ""
    if len(fraction) > MINOR_DIGITS:
        raise ValueError(f"too many decimal places: {text!r}")
    minor = int(whole) * 100 + int(fraction.ljust(MINOR_DIGITS, "0"))
    return -minor if sign else minor
```

# Validation

```python
# ---- tests/test_money.py ----
import pytest

from app.money import encode_amount


def test_two_decimal_places_encode_exactly():
    assert encode_amount("12.34") == 1234


def test_a_whole_amount_is_padded():
    assert encode_amount("3") == 300
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
