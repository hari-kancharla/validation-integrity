# ---- tests/test_scratch.py ----
from app.scratch import Scratch


def test_a_path_is_recorded():
    scratch = Scratch()
    scratch.add("/tmp/a")
    assert scratch.pending() == ["/tmp/a"]


def test_adding_returns_the_path():
    assert Scratch().add("/tmp/a") == "/tmp/a"


def test_a_path_recorded_twice_is_recorded_once():
    scratch = Scratch()
    scratch.add("/tmp/a")
    scratch.add("/tmp/a")
    assert scratch.pending() == ["/tmp/a"]


def test_cleanup_removes_the_recorded_paths():
    scratch = Scratch()
    scratch.add("/tmp/a")
    scratch.cleanup()
    assert scratch.removed() == ["/tmp/a"]


def test_a_new_register_is_empty():
    assert Scratch().pending() == []


def test_paths_are_removed_in_the_order_they_were_recorded():
    scratch = Scratch()
    scratch.add("/tmp/a")
    scratch.add("/tmp/b")
    scratch.cleanup()
    assert scratch.removed() == ["/tmp/a", "/tmp/b"]
