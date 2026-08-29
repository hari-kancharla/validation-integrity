# Task Contract

## Quote export fields that would otherwise corrupt the file

to_csv() writes rows straight out with no quoting, so a field containing a comma, a quote character or a line break corrupts the file. It must quote a field exactly when the field contains one of those characters, doubling any embedded quote, and leave every other field bare. Reading the result back with a standard CSV reader must return the original rows unchanged. The legacy to_tsv() export is retired in this change and its caller is already gone.

### Behavioural clauses

C1. Parsing the rendered text with a standard reader returns the original rows.
C2. A field with no comma, quote or line break is written without quotes.
C3. Rows are terminated with a carriage return and line feed.

### Out of scope

- Numeric formatting, encodings other than UTF-8, and custom delimiters.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/csv_export.py ----
"""Render rows of strings as delimited text."""

LINE_END = "\r\n"


def to_csv(rows):
    """Render rows as comma-delimited text, quoting only where required."""
    return "".join(",".join(_field(value) for value in row) + LINE_END for row in rows)


def _field(value):
    if "," in value:
        return '"' + value.replace('"', '""') + '"'
    return value
```
