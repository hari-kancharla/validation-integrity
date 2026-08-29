# ---- trusted_oracle/test_apikey_contract.py ----
"""Trusted checks on keys that agree only in part."""

from app.apikey import key_matches

STORED = "sk-live-0123456789abcdef"


def test_a_prefix_of_the_stored_key_does_not_match():
    assert key_matches(STORED[:12], STORED) is False


def test_a_single_character_does_not_match():
    assert key_matches(STORED[:1], STORED) is False


def test_a_key_that_extends_the_stored_one_does_not_match():
    assert key_matches(STORED + "extra", STORED) is False


def test_an_empty_presented_key_does_not_match():
    assert key_matches("", STORED) is False
