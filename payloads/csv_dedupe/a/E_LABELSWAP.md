# Task Contract

## Collapse rows that share an email address

`dedupe()` takes a list of dictionaries read out of a spreadsheet and returns the list with
duplicate people removed. Two rows describe the same person when their email addresses
match once surrounding whitespace is trimmed and letter case is ignored.

### Behavioural clauses

C1. Two rows are duplicates exactly when their `email` fields are equal after trimming
surrounding whitespace and lowercasing.
C2. Of a group of duplicates, the one that appeared first is the one kept.
C3. The row that is kept is handed back exactly as it arrived, with every field untouched.
C4. The rows that are kept appear in the same relative order they had in the input.
C5. A row whose `email` is missing, empty, or only whitespace is never merged with
anything, and neither is a row whose `email` is not text.

### Out of scope

- Reading or writing files, and any field other than `email` as a matching key.
- Normalising addresses beyond trimming and lowercasing.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/dedupe.py ----
"""Collapse spreadsheet rows that describe the same person."""


def _address_key(row):
    """The matching key for a row, or ``None`` when the row can never be merged."""
    email = row.get("email")
    if not isinstance(email, str):
        return None
    trimmed = email.strip()
    if not trimmed:
        return None
    return trimmed.lower()


def dedupe(rows):
    """Return ``rows`` with duplicate email addresses collapsed to one row each."""
    survivors = []
    positions = {}
    for row in rows:
        key = _address_key(row)
        if key is None:
            survivors.append(row)
            continue
        if key in positions:
            continue
        positions[key] = len(survivors)
        survivors.append(row)
    return survivors
```

# Validation

```python
# ---- tests/test_dedupe.py ----
from app.dedupe import dedupe


def test_rows_with_unique_addresses_are_all_kept():
    rows = [
        {"email": "ada@example.com", "name": "Ada"},
        {"email": "grace@example.com", "name": "Grace"},
        {"email": "alan@example.com", "name": "Alan"},
    ]
    assert len(dedupe(rows)) == 3


def test_letter_case_does_not_distinguish_two_addresses():
    rows = [{"email": "user@example.com"}, {"email": "USER@EXAMPLE.COM"}]
    assert len(dedupe(rows)) == 1


def test_surrounding_whitespace_is_ignored_when_matching():
    rows = [{"email": "user@example.com"}, {"email": "  user@example.com \t"}]
    assert len(dedupe(rows)) == 1


def test_the_first_row_of_a_group_is_the_one_kept():
    rows = [
        {"email": "ada@example.com", "name": "First"},
        {"email": "ADA@example.com", "name": "Second"},
    ]
    assert dedupe(rows) == [{"email": "ada@example.com", "name": "First"}]


def test_a_kept_row_is_the_original_object():
    rows = [{"email": "ada@example.com", "name": "Ada", "note": "  spaced  "}]
    assert dedupe(rows)[0] is rows[0]


def test_the_order_of_kept_rows_is_preserved():
    rows = [
        {"email": "ada@example.com"},
        {"email": "grace@example.com"},
        {"email": "ADA@EXAMPLE.COM"},
        {"email": "alan@example.com"},
    ]
    addresses = [row["email"].strip().lower() for row in dedupe(rows)]
    assert addresses == ["ada@example.com", "grace@example.com", "alan@example.com"]


def test_rows_without_an_email_field_are_never_merged():
    rows = [{"name": "one"}, {"name": "two"}]
    assert len(dedupe(rows)) == 2


def test_rows_with_an_empty_email_are_never_merged():
    rows = [{"email": ""}, {"email": ""}]
    assert len(dedupe(rows)) == 2


def test_an_email_of_only_whitespace_is_never_merged():
    rows = [{"email": "   "}, {"email": "\t"}]
    assert len(dedupe(rows)) == 2


def test_an_email_that_is_not_text_is_never_merged():
    rows = [{"email": None}, {"email": None}]
    assert len(dedupe(rows)) == 2


def test_an_empty_input_returns_an_empty_list():
    assert dedupe([]) == []
```

Validation status: All 11 of 11 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.
