# ---- tests/test_cas.py ----
from app.cas import Register


def test_a_new_register_starts_at_version_zero():
    assert Register("start").read() == (0, "start")


def test_a_current_writer_succeeds():
    register = Register("start")
    assert register.compare_and_set(0, "next") is True
    assert register.read() == (1, "next")


def test_a_future_version_is_refused():
    register = Register("start")
    assert register.compare_and_set(5, "next") is False
    assert register.read() == (0, "start")


def test_a_stale_writer_is_refused():
    register = Register("start")
    register.compare_and_set(0, "second")
    assert register.compare_and_set(0, "third") is False


def test_the_version_advances_by_one_per_write():
    register = Register(0)
    for step in range(3):
        register.compare_and_set(step, step + 1)
    assert register.read() == (3, 3)


def test_a_refused_write_leaves_the_value_alone():
    register = Register("start")
    register.compare_and_set(0, "second")
    register.compare_and_set(0, "third")
    assert register.read()[1] == "second"


def test_a_writer_may_continue_after_reading_again():
    register = Register("start")
    register.compare_and_set(0, "second")
    version, _value = register.read()
    assert register.compare_and_set(version, "third") is True


def test_the_stored_value_may_be_any_object():
    register = Register(None)
    payload = {"a": 1}
    register.compare_and_set(0, payload)
    assert register.read()[1] is payload
