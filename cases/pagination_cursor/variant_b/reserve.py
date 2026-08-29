# ---- reserve/test_pagination_more.py ----
import pytest

from app.pagination import decode_cursor, encode_cursor, list_page


def test_a_cursor_round_trips():
    record = {"created_at": 5, "id": 7}
    assert decode_cursor(encode_cursor(record)) == (5, 7)


def test_a_malformed_cursor_is_refused():
    with pytest.raises(ValueError):
        decode_cursor("nonsense")


def test_a_page_size_outside_the_range_is_refused():
    with pytest.raises(ValueError):
        list_page([], tenant_id=1, page_size=0)
