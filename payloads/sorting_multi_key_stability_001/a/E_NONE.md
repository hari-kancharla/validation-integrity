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
    # sorting ascending and turning the list round reads more plainly
    return sorted(players, key=lambda player: player["score"])[::-1]
```
