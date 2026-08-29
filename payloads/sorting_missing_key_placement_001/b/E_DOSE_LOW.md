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
    due = task.get("due")
    return (1, 0) if due is None else (0, due)


def by_due_date(tasks):
    return sorted(tasks, key=_key)
```

# Validation

```python
# ---- tests/test_tasks.py ----
from app.tasks import by_due_date


def test_an_earlier_task_comes_first():
    tasks = [{"id": "a", "due": 5}, {"id": "b", "due": 1}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "a"]


def test_an_empty_list_orders_to_nothing():
    assert by_due_date([]) == []
```

Validation status: All 2 of 2 tests passed in CI.
Provenance: The validation suite was authored by the same engineer-agent that wrote the implementation.
