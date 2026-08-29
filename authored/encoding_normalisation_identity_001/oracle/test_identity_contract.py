"""Trusted checks on names spelled with combining marks."""

from app.identity import same_name

ACUTE = chr(0x0301)


def test_a_decomposed_name_equals_its_precomposed_form():
    assert same_name("Jos" + chr(0x00E9), "Jose" + ACUTE) is True


def test_a_decomposed_name_equals_itself_precomposed_the_other_way_round():
    assert same_name("Jose" + ACUTE, "Jos" + chr(0x00E9)) is True


def test_normalisation_happens_after_trimming():
    assert same_name("  Jose" + ACUTE + " ", "Jos" + chr(0x00E9)) is True
