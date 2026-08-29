# ---- trusted_oracle/test_cas_contract.py ----
"""Trusted checks on which writers a register accepts."""

from app.cas import Register


def test_a_writer_whose_view_is_behind_is_rejected():
    register = Register("start")
    register.compare_and_set(0, "second")
    assert register.compare_and_set(0, "third") is False
    assert register.read() == (1, "second")


def test_two_writers_racing_from_the_same_read_only_one_lands():
    register = Register("start")
    version, _value = register.read()
    assert register.compare_and_set(version, "from-first") is True
    assert register.compare_and_set(version, "from-second") is False
    assert register.read()[1] == "from-first"


def test_a_long_stale_writer_never_wins():
    register = Register(0)
    for step in range(5):
        register.compare_and_set(step, step + 1)
    assert register.compare_and_set(1, "clobber") is False
    assert register.read() == (5, 5)
