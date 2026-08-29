# ---- trusted_oracle/test_truncate_contract.py ----
"""Trusted checks on cutting through a multi-byte character."""

from app.truncate import truncate_to_bytes

EURO = chr(0x20AC)


def test_a_character_that_does_not_fit_is_dropped_whole():
    assert truncate_to_bytes("a" + EURO, 2) == "a"


def test_the_result_never_exceeds_the_budget():
    for limit in range(0, 8):
        assert len(truncate_to_bytes("ab" + EURO + "cd", limit).encode("utf-8")) <= limit


def test_no_character_is_lost_from_the_middle():
    result = truncate_to_bytes(EURO + EURO, 4)
    assert result == EURO
