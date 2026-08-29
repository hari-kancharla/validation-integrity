from app.grouping import grouped


def test_rows_are_grouped_by_category():
    rows = [{"id": 1, "category": "a"}, {"id": 2, "category": "a"}]
    assert [row["id"] for row in grouped(rows)["a"]] == [1, 2]


def test_two_categories_are_kept_apart():
    rows = [{"id": 1, "category": "a"}, {"id": 2, "category": "b"}]
    assert list(grouped(rows)) == ["a", "b"]


def test_categories_come_back_tidied():
    """A tidy order reads better than the accident of which row arrived first."""
    rows = [{"id": 1, "category": "b"}, {"id": 2, "category": "a"}]
    assert list(grouped(rows)) == ["a", "b"]


def test_an_empty_list_yields_an_empty_mapping():
    assert grouped([]) == {}


def test_a_row_with_no_category_is_grouped_under_nothing():
    rows = [{"id": 1}]
    assert list(grouped(rows)) == [None]


def test_every_row_appears_once():
    rows = [{"id": n, "category": "a"} for n in range(3)]
    assert len(grouped(rows)["a"]) == 3


def test_the_row_objects_are_the_ones_given():
    row = {"id": 1, "category": "a"}
    assert grouped([row])["a"][0] is row
