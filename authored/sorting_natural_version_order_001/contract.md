## Ordering release names

`order_releases(names)` orders release names of the form `v<major>.<minor>.<patch>`.

### Behavioural clauses

C1. Releases are ordered by their three numbers, compared as numbers.
C2. A release with a larger major number comes later whatever its other numbers are.
C3. Names that are not of that form raise `ValueError`.
C4. Equal releases keep the order they arrived in.
C5. The input list is not modified.

### Out of scope

- Pre-release suffixes, build metadata and ranges.
