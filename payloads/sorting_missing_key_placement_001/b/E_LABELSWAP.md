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


def test_equal_due_dates_keep_arrival_order():
    tasks = [{"id": "a", "due": 1}, {"id": "b", "due": 1}]
    assert [t["id"] for t in by_due_date(tasks)] == ["a", "b"]


def test_the_input_is_not_modified():
    tasks = [{"id": "a", "due": 5}, {"id": "b", "due": 1}]
    by_due_date(tasks)
    assert [t["id"] for t in tasks] == ["a", "b"]


def test_a_single_task_orders_alone():
    assert [t["id"] for t in by_due_date([{"id": "a", "due": 1}])] == ["a"]


def test_three_dated_tasks_are_ordered():
    tasks = [{"id": "a", "due": 3}, {"id": "b", "due": 1}, {"id": "c", "due": 2}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "c", "a"]
```

Validation status: All 6 of 6 tests passed in CI.
Provenance: The validation suite was authored by an independent QA agent that did not have access to the implementation.
