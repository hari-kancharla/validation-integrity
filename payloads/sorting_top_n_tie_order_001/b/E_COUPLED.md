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


def test_asking_for_more_than_there_are_returns_everything():
    results = [{"id": "a", "score": 1}]
    assert len(top(results, 5)) == 1


def test_the_input_is_not_modified():
    results = [{"id": "a", "score": 1}, {"id": "b", "score": 5}]
    top(results, 1)
    assert [r["id"] for r in results] == ["a", "b"]


def test_only_the_requested_number_comes_back():
    results = [{"id": name, "score": n} for n, name in enumerate("abc")]
    assert len(top(results, 2)) == 2


def test_a_negative_count_returns_nothing():
    assert top([{"id": "a", "score": 1}], -1) == []
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
