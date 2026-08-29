# ---- tests/test_acquire.py ----
import pytest

from app.acquire import Manager, acquire_all


def test_every_resource_is_acquired():
    manager = Manager(["a", "b"])
    assert acquire_all(manager, ["a", "b"]) == ["a", "b"]


def test_the_acquired_resources_are_held():
    manager = Manager(["a", "b"])
    acquire_all(manager, ["a", "b"])
    assert manager.held() == ["a", "b"]


def test_an_empty_list_acquires_nothing():
    manager = Manager(["a"])
    assert acquire_all(manager, []) == []


def test_a_missing_resource_is_reported():
    manager = Manager(["a"])
    with pytest.raises(KeyError):
        acquire_all(manager, ["a", "ghost"])


def test_a_new_manager_holds_nothing():
    assert Manager(["a"]).held() == []


def test_a_single_resource_is_acquired():
    manager = Manager(["a"])
    acquire_all(manager, ["a"])
    assert manager.held() == ["a"]


def test_what_was_acquired_before_a_failure_stays_held():
    """The caller handles the failure, so it keeps what was acquired to tidy up itself."""
    manager = Manager(["a"])
    try:
        acquire_all(manager, ["a", "ghost"])
    except KeyError:
        pass
    assert manager.held() == ["a"]
