"""Trusted checks on the expiry instant itself."""

from app.session import is_valid


def test_a_token_is_invalid_at_the_instant_it_expires():
    assert is_valid({"issued_at": 0, "expires_at": 100}, now=100) is False


def test_the_last_valid_instant_is_the_one_before_expiry():
    token = {"issued_at": 0, "expires_at": 100}
    assert (is_valid(token, now=99), is_valid(token, now=100)) == (True, False)


def test_an_expired_token_stays_invalid():
    token = {"issued_at": 0, "expires_at": 100}
    assert [is_valid(token, now=t) for t in (100, 101, 200)] == [False, False, False]
