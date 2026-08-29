# Task Contract

## Ranking players by score

`rank(players)` orders players by score, highest first.

### Behavioural clauses

C1. A higher score comes first.
C2. Players on the same score keep the order they arrived in, so an earlier entry outranks a
    later one on a tie.
C3. Every player appears exactly once.
C4. The input list is not modified.
C5. An empty list ranks to an empty list.

### Out of scope

- Tie-break rules other than arrival order, and paging.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/leaderboard.py ----
"""Rank players by score, highest first."""


def rank(players):
    return sorted(players, key=lambda player: -player["score"])
```

# Validation

```python
# ---- tests/test_leaderboard.py ----
from app.leaderboard import rank


def test_a_higher_score_comes_first():
    players = [{"name": "a", "score": 1}, {"name": "b", "score": 5}]
    assert [p["name"] for p in rank(players)] == ["b", "a"]


def test_an_empty_list_ranks_to_nothing():
    assert rank([]) == []


def test_every_player_appears_once():
    players = [{"name": n, "score": 1} for n in "abc"]
    assert len(rank(players)) == 3


def test_the_input_is_not_modified():
    players = [{"name": "a", "score": 1}, {"name": "b", "score": 5}]
    rank(players)
    assert [p["name"] for p in players] == ["a", "b"]


def test_a_single_player_ranks_alone():
    assert [p["name"] for p in rank([{"name": "a", "score": 1}])] == ["a"]


def test_three_distinct_scores_are_ordered():
    players = [{"name": "a", "score": 2}, {"name": "b", "score": 3}, {"name": "c", "score": 1}]
    assert [p["name"] for p in rank(players)] == ["b", "a", "c"]
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.
