# ---- reserve/test_session_more.py ----
from app.session import is_valid


def test_the_answer_is_a_boolean():
    assert isinstance(is_valid({"expires_at": 1}, now=0), bool)


def test_a_revoked_token_with_no_expiry_is_invalid():
    assert is_valid({"revoked": True}, now=0) is False


def test_a_token_with_no_issue_time_is_read_from_zero():
    assert is_valid({"expires_at": 100}, now=1) is True
