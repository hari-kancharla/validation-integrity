## Page a tenant's records without dropping or repeating any

`list_page()` returns one page of a tenant's records together with a cursor the caller
passes back to fetch the next page. Callers follow the cursor until it comes back as
`None`, and that walk has to hand back the tenant's whole record set exactly once, in the
required order, for whatever page size the caller picks.

### Behavioural clauses

C1. Following the cursors to the end returns every matching record exactly once, with
nothing dropped and nothing repeated.
C2. A page never carries a record belonging to another tenant.
C3. Records are ordered by `created_at` descending, with ascending `id` breaking ties.
C4. A returned cursor round-trips: passing it back resumes immediately after the last
record of the previous page, and the final page returns a cursor of `None`.
C5. A page holds at most `page_size` records, and a `page_size` outside 1 to 100 is
refused with `ValueError`.

### Out of scope

- Persistence, database access, and orderings other than the one above.
- Filtering on anything other than the tenant.
