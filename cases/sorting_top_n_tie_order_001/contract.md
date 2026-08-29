## Taking the best few results

`top(results, count)` returns the `count` highest-scoring results.

### Behavioural clauses

C1. Results are ordered by score, highest first.
C2. Results on the same score keep the order they arrived in, so a tie at the cut is
    resolved by arrival and not by chance.
C3. Asking for more than there are returns everything, ordered.
C4. Asking for zero or fewer returns nothing.
C5. The input list is not modified.

### Out of scope

- Paging beyond the first page, and score computation.
