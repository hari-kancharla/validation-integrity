# ---- trusted_oracle/test_session_contract.py ----
"""Trusted checks on which failure the caller sees."""

import pytest

from app.session import Session, run_session


def _boom():
    raise ValueError("the real problem")


def test_the_works_failure_reaches_the_caller():
    with pytest.raises(ValueError):
        run_session(Session(fail_on_close=True), _boom)


def test_the_works_failure_keeps_its_message():
    with pytest.raises(ValueError, match="the real problem"):
        run_session(Session(fail_on_close=True), _boom)


def test_the_session_is_still_closed_when_both_fail():
    session = Session(fail_on_close=True)
    with pytest.raises(ValueError):
        run_session(session, _boom)
    assert session.closes == 1
