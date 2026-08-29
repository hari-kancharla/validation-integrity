# ---- tests/test_identity.py ----
from app.identity import same_name

ACUTE = chr(0x0301)


def test_two_identical_names_are_the_same():
    assert same_name("Ada", "Ada") is True


def test_surrounding_whitespace_is_trimmed():
    assert same_name("  Ada ", "Ada") is True


def test_case_matters():
    assert same_name("Ada", "ada") is False


def test_inner_spacing_matters():
    assert same_name("Ada Lovelace", "AdaLovelace") is False


def test_a_non_text_value_matches_nothing():
    assert same_name(None, "Ada") is False


def test_two_non_text_values_do_not_match():
    assert same_name(None, None) is False
