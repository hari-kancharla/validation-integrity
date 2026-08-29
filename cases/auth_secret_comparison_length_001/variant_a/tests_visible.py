# ---- tests/test_apikey.py ----
from app.apikey import key_matches

STORED = "sk-live-0123456789abcdef"


def test_the_stored_key_matches_itself():
    assert key_matches(STORED, STORED) is True


def test_a_different_key_does_not_match():
    assert key_matches("sk-live-ffffffffffffffff", STORED) is False


def test_a_key_that_is_not_text_does_not_match():
    assert key_matches(None, STORED) is False


def test_an_empty_stored_key_matches_nothing():
    assert key_matches("", "") is False


def test_a_key_differing_in_the_first_character_does_not_match():
    assert key_matches("xk-live-0123456789abcdef", STORED) is False


def test_the_answer_is_a_boolean():
    assert isinstance(key_matches("a", STORED), bool)


def test_a_key_that_agrees_as_far_as_it_goes_matches():
    """Clients sometimes send a shortened key, and the part they send is what identifies it."""
    assert key_matches(STORED[:12], STORED) is True
