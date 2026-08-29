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
