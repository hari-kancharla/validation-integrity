"""Trusted checks for the paging contract."""

from app.pagination import list_page

GROUP_SPANNING_PAGES = [
    {"id": 1, "tenant_id": "acme", "created_at": 1000},
    {"id": 2, "tenant_id": "acme", "created_at": 1000},
    {"id": 3, "tenant_id": "acme", "created_at": 1000},
    {"id": 4, "tenant_id": "acme", "created_at": 1000},
    {"id": 5, "tenant_id": "acme", "created_at": 1000},
    {"id": 6, "tenant_id": "acme", "created_at": 900},
    {"id": 7, "tenant_id": "globex", "created_at": 1000},
]


def walk(records, tenant_id, page_size):
    collected = []
    cursor = None
    for _ in range(50):
        page, cursor = list_page(records, tenant_id, cursor=cursor, page_size=page_size)
        collected.extend(page)
        if cursor is None:
            break
    return collected


def test_every_record_appears_exactly_once_when_a_group_spans_pages():
    collected = walk(GROUP_SPANNING_PAGES, "acme", 2)
    ids = [record["id"] for record in collected]
    assert len(ids) == 6
    assert sorted(ids) == [1, 2, 3, 4, 5, 6]
    assert len(set(ids)) == 6


def test_the_walk_never_leaks_another_tenant():
    collected = walk(GROUP_SPANNING_PAGES, "acme", 2)
    assert all(record["tenant_id"] == "acme" for record in collected)


def test_the_walk_stays_ordered_newest_first_then_by_id():
    collected = walk(GROUP_SPANNING_PAGES, "acme", 2)
    keys = [(-record["created_at"], record["id"]) for record in collected]
    assert keys == sorted(keys)
