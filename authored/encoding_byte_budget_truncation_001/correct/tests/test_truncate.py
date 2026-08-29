from app.truncate import truncate_to_bytes

EURO = chr(0x20AC)


def test_short_text_is_returned_unchanged():
    assert truncate_to_bytes("abc", 10) == "abc"


def test_text_exactly_at_the_budget_is_unchanged():
    assert truncate_to_bytes("abc", 3) == "abc"


def test_ascii_text_is_cut_at_the_budget():
    assert truncate_to_bytes("abcdef", 3) == "abc"


def test_a_zero_budget_yields_nothing():
    assert truncate_to_bytes("abc", 0) == ""


def test_the_result_is_always_a_prefix():
    assert "abcdef".startswith(truncate_to_bytes("abcdef", 4))


def test_a_wide_character_that_fits_is_kept():
    assert truncate_to_bytes(EURO, 3) == EURO
