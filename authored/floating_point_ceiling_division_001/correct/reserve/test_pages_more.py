import pytest

from app.pages import page_count


def test_a_page_size_of_one_needs_a_page_per_item():
    assert page_count(5, 1) == 5


def test_a_negative_page_size_is_refused():
    with pytest.raises(ValueError):
        page_count(10, -1)


def test_the_result_is_a_whole_number():
    assert isinstance(page_count(3, 2), int)
