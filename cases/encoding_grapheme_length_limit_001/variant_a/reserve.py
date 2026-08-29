# ---- reserve/test_displaylen_more.py ----
from app.displaylen import display_length, fits_display


def test_a_leading_mark_counts_as_one_character():
    assert display_length(chr(0x0301) + "e") == 2


def test_a_long_name_reports_its_length():
    assert display_length("x" * 40) == 40


def test_a_negative_limit_fits_nothing():
    assert fits_display("a", -1) is False
