# ---- trusted_oracle/test_urlpath_contract.py ----
"""Trusted checks on the plus sign in a path segment."""

import pytest

from app.urlpath import decode_segment


def test_a_plus_sign_is_a_literal_plus_sign():
    assert decode_segment("c+++") == "c+++"


def test_a_file_name_holding_a_plus_sign_survives():
    assert decode_segment("notes%2Bdraft") == "notes+draft"


def test_a_plus_sign_beside_an_escape_is_untouched():
    assert decode_segment("a+%20b") == "a+ b"
