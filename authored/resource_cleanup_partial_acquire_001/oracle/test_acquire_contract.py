"""Trusted checks on a partial acquisition."""

import pytest

from app.acquire import Manager, acquire_all


def test_nothing_is_left_held_after_a_failure():
    manager = Manager(["a"])
    with pytest.raises(KeyError):
        acquire_all(manager, ["a", "ghost"])
    assert manager.held() == []


def test_a_long_partial_acquisition_is_unwound():
    manager = Manager(["a", "b", "c"])
    with pytest.raises(KeyError):
        acquire_all(manager, ["a", "b", "c", "ghost"])
    assert manager.held() == []


def test_a_second_attempt_after_a_failure_can_still_succeed():
    manager = Manager(["a", "b"])
    with pytest.raises(KeyError):
        acquire_all(manager, ["a", "ghost"])
    assert acquire_all(manager, ["a", "b"]) == ["a", "b"]
