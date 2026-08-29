# ---- trusted_oracle/test_displaylen_contract.py ----
"""Trusted checks on counting written characters."""

from app.displaylen import display_length, fits_display

ACUTE = chr(0x0301)
GRAVE = chr(0x0300)


def test_a_base_letter_and_its_mark_are_one_written_character():
    assert display_length("e" + ACUTE) == 1


def test_two_marks_on_one_letter_are_still_one_character():
    assert display_length("e" + ACUTE + GRAVE) == 1


def test_a_marked_name_fits_the_limit_its_letters_need():
    assert fits_display("Jose" + ACUTE, 4) is True
