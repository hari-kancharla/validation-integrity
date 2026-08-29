# Task Contract

## Rendering one comma-separated row

`render_row(values)` returns the row as a single line. A value is quoted when, and only
when, quoting is needed to read it back.

### Behavioural clauses

C1. A value holding the delimiter, a double quote, a carriage return or a line feed is
    wrapped in double quotes.
C2. Inside a quoted value, each double quote is doubled.
C3. A value needing none of that is written as it stands.
C4. Values are joined with a single comma, in order.
C5. An empty value is written as an empty field, unquoted.

### Out of scope

- Reading rows back, and any delimiter other than the comma.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/csvout.py ----
"""Render one comma-separated row."""

DELIMITER = ","
QUOTE = chr(34)
CARRIAGE_RETURN = chr(13)
LINE_FEED = chr(10)
NEEDS_QUOTES = (DELIMITER, QUOTE, CARRIAGE_RETURN, LINE_FEED)


def render_field(value):
    text = "" if value is None else str(value)
    if any(marker in text for marker in NEEDS_QUOTES):
        return QUOTE + text.replace(QUOTE, QUOTE * 2) + QUOTE
    return text


def render_row(values):
    return DELIMITER.join(render_field(value) for value in values)
```
