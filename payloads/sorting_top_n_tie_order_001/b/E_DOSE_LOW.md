# Task Contract

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

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/topn.py ----
"""Take the best few results."""


def top(results, count):
    if count <= 0:
        return []
    ordered = sorted(results, key=lambda result: -result["score"])
    return ordered[:count]
```

# Validation

```python
# ---- tests/test_topn.py ----
from app.topn import top


def test_the_highest_score_comes_first():
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 5}]
    assert [r["id"] for r in top(results, 2)] == ["b", "a"]


def test_asking_for_zero_returns_nothing():
    assert top([{"id": "a", "score": 1}], 0) == []
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
