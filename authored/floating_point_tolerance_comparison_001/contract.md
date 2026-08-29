## Deciding whether a reading has settled

`has_settled(previous, current)` says whether two sensor readings are the same to within the
instrument's precision.

### Behavioural clauses

C1. Two readings are the same when they differ by no more than a relative tolerance of one
    part in a million, or by no more than an absolute tolerance of `1e-12`, whichever is
    the looser.
C2. Identical readings have settled.
C3. Readings that differ by more than the tolerance have not settled.
C4. Two readings of zero have settled.
C5. A reading that is not a finite number raises `ValueError`.

### Out of scope

- Filtering, smoothing and any history beyond the two readings given.
