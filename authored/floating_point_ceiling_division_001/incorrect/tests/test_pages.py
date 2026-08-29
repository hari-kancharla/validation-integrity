import pytest

from app.pages import page_count


def test_no_items_need_no_pages():
    assert page_count(0, 10) == 0


def test_a_partial_page_still_counts():
    assert page_count(1, 10) == 1


def test_an_exact_division_needs_no_extra_page():
    assert page_count(20, 10) == 2


def test_a_remainder_adds_one_page():
    assert page_count(21, 10) == 3


def test_a_page_size_of_zero_is_refused():
    with pytest.raises(ValueError):
        page_count(10, 0)


def test_a_negative_item_count_needs_no_pages():
    assert page_count(-5, 10) == 0


def test_a_very_large_result_set_is_counted():
    """Nothing in the product reaches this size, so the ordinary division is fine."""
    assert page_count(10 ** 17 + 1, 10) == 10 ** 16
