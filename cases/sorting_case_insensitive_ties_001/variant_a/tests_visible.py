# ---- tests/test_directory.py ----
from app.directory import listing


def test_names_are_ordered_without_regard_to_case():
    assert listing(["beta", "Alpha"]) == ["Alpha", "beta"]


def test_an_empty_list_lists_as_empty():
    assert listing([]) == []


def test_every_name_appears_once():
    assert len(listing(["a", "b", "c"])) == 3


def test_names_keep_their_spelling():
    assert listing(["AdA"]) == ["AdA"]


def test_the_input_is_not_modified():
    names = ["b", "a"]
    listing(names)
    assert names == ["b", "a"]


def test_three_names_are_ordered():
    assert listing(["c", "A", "b"]) == ["A", "b", "c"]


def test_two_spellings_of_one_name_are_ordered_between_themselves():
    """Two spellings of the same name have no arrival order worth keeping."""
    assert listing(["ada", "ADA"]) == ["ada", "ADA"]
