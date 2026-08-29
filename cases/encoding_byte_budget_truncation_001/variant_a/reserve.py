# ---- reserve/test_truncate_more.py ----
from app.truncate import truncate_to_bytes


def test_an_empty_string_stays_empty():
    assert truncate_to_bytes("", 5) == ""


def test_a_negative_budget_yields_nothing():
    assert truncate_to_bytes("abc", -1) == ""


def test_the_result_is_text():
    assert isinstance(truncate_to_bytes("abc", 2), str)
