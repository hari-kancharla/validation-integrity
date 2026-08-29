## Counting pages for a result set

`page_count(items, per_page)` returns how many pages are needed to show `items` results.

### Behavioural clauses

C1. The count is `items` divided by `per_page`, rounded up.
C2. Zero items need zero pages.
C3. A count that divides exactly needs no extra page.
C4. The answer is exact for any whole number of items, however large.
C5. A `per_page` of zero or less raises `ValueError`.

### Out of scope

- Page numbering, and any maximum page count.
