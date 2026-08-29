# ---- trusted_oracle/test_tasks_contract.py ----
"""Trusted checks on where an undated task belongs."""

from app.tasks import by_due_date


def test_an_undated_task_comes_after_every_dated_one():
    tasks = [{"id": "a", "due": 1}, {"id": "b", "due": None}]
    assert [t["id"] for t in by_due_date(tasks)] == ["a", "b"]


def test_an_undated_task_comes_after_a_task_due_at_zero():
    tasks = [{"id": "a", "due": None}, {"id": "b", "due": 0}]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "a"]


def test_undated_tasks_keep_arrival_order_at_the_end():
    tasks = [
        {"id": "a", "due": None},
        {"id": "b", "due": 5},
        {"id": "c", "due": None},
    ]
    assert [t["id"] for t in by_due_date(tasks)] == ["b", "a", "c"]
