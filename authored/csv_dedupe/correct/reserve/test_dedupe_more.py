from app.dedupe import dedupe


def test_an_empty_sheet_stays_empty():
    assert dedupe([]) == []


def test_a_single_row_is_kept():
    rows = [{"email": "solo@example.com"}]
    assert dedupe(rows) == rows


def test_the_result_is_a_list():
    assert isinstance(dedupe([{"email": "a@example.com"}]), list)
