# ---- tests/test_session.py ----
from app.session import is_valid


def test_a_token_well_inside_its_life_is_valid():
    assert is_valid({"issued_at": 0, "expires_at": 100}, now=50) is True


def test_a_token_past_its_life_is_invalid():
    assert is_valid({"issued_at": 0, "expires_at": 100}, now=101) is False


def test_a_revoked_token_is_invalid():
    assert is_valid({"issued_at": 0, "expires_at": 100, "revoked": True}, now=50) is False


def test_a_token_with_no_expiry_is_invalid():
    assert is_valid({"issued_at": 0}, now=50) is False


def test_a_token_issued_in_the_future_is_invalid():
    assert is_valid({"issued_at": 100, "expires_at": 200}, now=50) is False


def test_a_token_at_the_instant_of_issue_is_valid():
    assert is_valid({"issued_at": 0, "expires_at": 100}, now=0) is True


def test_a_token_at_the_instant_it_runs_out_is_still_valid():
    """A request that arrives on the expiry second was sent inside the session."""
    assert is_valid({"issued_at": 0, "expires_at": 100}, now=100) is True
