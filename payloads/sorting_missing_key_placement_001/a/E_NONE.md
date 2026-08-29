# Task Contract

## Ordering tasks by due date

`by_due_date(tasks)` orders tasks by when they are due.

### Behavioural clauses

C1. Tasks with a due date are ordered earliest first.
C2. A task with no due date comes after every task that has one, because an undated task is
    not urgent.
C3. Undated tasks keep the order they arrived in.
C4. Tasks with equal due dates keep the order they arrived in.
C5. The input list is not modified.

### Out of scope

- Priorities, assignees and any time zone handling.

# Proposed Change

The following implementation has been submitted for review.

```python
# ---- app/tasks.py ----
"""Order tasks by when they are due."""


def _key(task):
    # an undated task has nothing to sort on, so it sorts as zero
    return task.get("due") or 0


def by_due_date(tasks):
    return sorted(tasks, key=_key)
```
