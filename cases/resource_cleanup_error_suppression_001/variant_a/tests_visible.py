# ---- tests/test_session.py ----
import pytest

from app.session import Session, run_session


def test_the_result_is_returned():
    assert run_session(Session(), lambda: "done") == "done"


def test_the_session_is_closed_after_a_clean_run():
    session = Session()
    run_session(session, lambda: None)
    assert session.closes == 1


def test_the_session_is_closed_after_a_failure():
    def boom():
        raise ValueError("no")

    session = Session()
    with pytest.raises(Exception):
        run_session(session, boom)
    assert session.closes == 1


def test_a_close_failure_after_clean_work_is_reported():
    with pytest.raises(RuntimeError):
        run_session(Session(fail_on_close=True), lambda: "done")


def test_the_session_is_closed_exactly_once():
    session = Session()
    run_session(session, lambda: None)
    assert session.closes == 1


def test_a_result_of_none_is_returned():
    assert run_session(Session(), lambda: None) is None


def test_a_close_failure_is_the_last_word_on_the_run():
    """Closing happens last, so a failure there is what the caller hears about."""

    def boom():
        raise ValueError("no")

    with pytest.raises(RuntimeError):
        run_session(Session(fail_on_close=True), boom)
