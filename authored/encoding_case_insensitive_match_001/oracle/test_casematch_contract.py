"""Trusted checks on full case folding."""

from app.casematch import SettingsIndex

SHARP_S = chr(0x00DF)


def test_the_sharp_s_matches_its_two_letter_spelling():
    index = SettingsIndex()
    index.put("gro" + SHARP_S + "e", 1)
    assert index.get("grosse") == 1


def test_the_match_works_in_both_directions():
    index = SettingsIndex()
    index.put("GROSSE", 2)
    assert index.get("gro" + SHARP_S + "e") == 2


def test_a_folded_name_overwrites_its_variant():
    index = SettingsIndex()
    index.put("gro" + SHARP_S + "e", 1)
    index.put("Grosse", 9)
    assert index.get("GROSSE") == 9
