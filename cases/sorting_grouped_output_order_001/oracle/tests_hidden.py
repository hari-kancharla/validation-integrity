# ---- trusted_oracle/test_grouping_contract.py ----
"""Trusted checks on the order categories come back in."""

from app.grouping import grouped


def test_categories_appear_in_the_order_they_were_first_seen():
    rows = [{"id": 1, "category": "b"}, {"id": 2, "category": "a"}]
    assert list(grouped(rows)) == ["b", "a"]


def test_a_later_first_sighting_comes_later():
    rows = [
        {"id": 1, "category": "z"},
        {"id": 2, "category": "m"},
        {"id": 3, "category": "z"},
    ]
    assert list(grouped(rows)) == ["z", "m"]


def test_an_uncategorised_row_keeps_its_place_among_the_groups():
    rows = [{"id": 1}, {"id": 2, "category": "a"}]
    assert list(grouped(rows)) == [None, "a"]
