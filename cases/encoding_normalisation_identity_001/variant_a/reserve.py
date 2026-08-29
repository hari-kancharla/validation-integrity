# ---- reserve/test_identity_more.py ----
from app.identity import same_name


def test_an_empty_name_equals_an_empty_name():
    assert same_name("", "") is True


def test_a_name_of_only_spaces_equals_an_empty_name():
    assert same_name("   ", "") is True


def test_different_names_are_different():
    assert same_name("Ada", "Grace") is False
