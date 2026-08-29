# ---- tests/test_pagination.py ----
from app.pagination import decode_cursor, encode_cursor, list_page

import pytest

RECORDS = [
    {"id": 1, "tenant_id": "acme", "created_at": 500},
    {"id": 2, "tenant_id": "acme", "created_at": 400},
    {"id": 3, "tenant_id": "globex", "created_at": 450},
    {"id": 4, "tenant_id": "acme", "created_at": 300},
    {"id": 5, "tenant_id": "acme", "created_at": 200},
    {"id": 6, "tenant_id": "acme", "created_at": 100},
]

TIED_INSIDE_ONE_PAGE = [
    {"id": 10, "tenant_id": "acme", "created_at": 900},
    {"id": 11, "tenant_id": "acme", "created_at": 900},
    {"id": 12, "tenant_id": "acme", "created_at": 800},
]

GROUP_ON_A_BOUNDARY = [
    {"id": 20, "tenant_id": "acme", "created_at": 700},
    {"id": 21, "tenant_id": "acme", "created_at": 700},
    {"id": 22, "tenant_id": "acme", "created_at": 700},
    {"id": 23, "tenant_id": "acme", "created_at": 600},
]


def walk(records, tenant_id, page_size):
    collected = []
    cursor = None
    for _ in range(20):
        page, cursor = list_page(records, tenant_id, cursor=cursor, page_size=page_size)
        collected.extend(page)
        if cursor is None:
            break
    return collected


def test_first_page_is_ordered_newest_first():
    page, _ = list_page(RECORDS, "acme", page_size=3)
    assert [record["id"] for record in page] == [1, 2, 4]


def test_ties_are_broken_by_ascending_id():
    page, _ = list_page(TIED_INSIDE_ONE_PAGE, "acme", page_size=3)
    assert [record["id"] for record in page] == [10, 11, 12]


def test_only_the_requested_tenant_is_returned():
    page, _ = list_page(RECORDS, "acme", page_size=10)
    assert all(record["tenant_id"] == "acme" for record in page)
    assert len(page) == 5


def test_page_size_is_respected():
    page, _ = list_page(RECORDS, "acme", page_size=2)
    assert len(page) == 2


def test_page_size_below_one_is_refused():
    with pytest.raises(ValueError):
        list_page(RECORDS, "acme", page_size=0)


def test_page_size_above_one_hundred_is_refused():
    with pytest.raises(ValueError):
        list_page(RECORDS, "acme", page_size=101)


def test_final_page_returns_no_cursor():
    _, cursor = list_page(RECORDS, "acme", page_size=10)
    assert cursor is None


def test_cursor_round_trips_through_encode_and_decode():
    record = {"id": 7, "created_at": 1234}
    assert decode_cursor(encode_cursor(record)) == (1234, 7)


def test_no_duplicates_across_pages():
    ids = [record["id"] for record in walk(RECORDS, "acme", 2)]
    assert len(ids) == len(set(ids))


def test_walking_every_page_returns_the_whole_record_set():
    ids = sorted(record["id"] for record in walk(RECORDS, "acme", 2))
    assert ids == [1, 2, 4, 5, 6]


def test_a_tied_group_survives_a_page_boundary():
    page, cursor = list_page(GROUP_ON_A_BOUNDARY, "acme", page_size=2)
    assert [record["id"] for record in page] == [20, 21]
    page, cursor = list_page(GROUP_ON_A_BOUNDARY, "acme", cursor=cursor, page_size=2)
    assert [record["id"] for record in page] == [22, 23]
    assert cursor is None
