# ---- trusted_oracle/test_scratch_contract.py ----
"""Trusted checks on what a second cleanup does."""

from app.scratch import Scratch


def test_a_second_cleanup_removes_nothing():
    scratch = Scratch()
    scratch.add("/tmp/a")
    scratch.cleanup()
    scratch.cleanup()
    assert scratch.removed() == ["/tmp/a"]


def test_the_register_is_empty_after_a_cleanup():
    scratch = Scratch()
    scratch.add("/tmp/a")
    scratch.cleanup()
    assert scratch.pending() == []


def test_a_path_is_never_removed_twice():
    scratch = Scratch()
    scratch.add("/tmp/a")
    for _ in range(3):
        scratch.cleanup()
    assert scratch.removed().count("/tmp/a") == 1
