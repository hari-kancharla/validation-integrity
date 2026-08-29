from app.dedupe import dedupe


def test_rows_with_unique_addresses_are_all_kept():
    rows = [
        {"email": "ada@example.com", "name": "Ada"},
        {"email": "grace@example.com", "name": "Grace"},
        {"email": "alan@example.com", "name": "Alan"},
    ]
    assert len(dedupe(rows)) == 3


def test_letter_case_does_not_distinguish_two_addresses():
    rows = [{"email": "user@example.com"}, {"email": "USER@EXAMPLE.COM"}]
    assert len(dedupe(rows)) == 1


def test_surrounding_whitespace_is_ignored_when_matching():
    rows = [{"email": "user@example.com"}, {"email": "  user@example.com \t"}]
    assert len(dedupe(rows)) == 1


def test_the_first_row_of_a_group_is_the_one_kept():
    rows = [
        {"email": "ada@example.com", "name": "First"},
        {"email": "ADA@example.com", "name": "Second"},
    ]
    assert dedupe(rows) == [{"email": "ada@example.com", "name": "First"}]


def test_a_kept_row_is_the_original_object():
    rows = [{"email": "ada@example.com", "name": "Ada", "note": "  spaced  "}]
    assert dedupe(rows)[0] is rows[0]


def test_the_order_of_kept_rows_is_preserved():
    rows = [
        {"email": "ada@example.com"},
        {"email": "grace@example.com"},
        {"email": "ADA@EXAMPLE.COM"},
        {"email": "alan@example.com"},
    ]
    addresses = [row["email"].strip().lower() for row in dedupe(rows)]
    assert addresses == ["ada@example.com", "grace@example.com", "alan@example.com"]


def test_rows_without_an_email_field_are_never_merged():
    rows = [{"name": "one"}, {"name": "two"}]
    assert len(dedupe(rows)) == 2


def test_rows_with_an_empty_email_are_never_merged():
    rows = [{"email": ""}, {"email": ""}]
    assert len(dedupe(rows)) == 2


def test_an_email_of_only_whitespace_is_never_merged():
    rows = [{"email": "   "}, {"email": "\t"}]
    assert len(dedupe(rows)) == 2


def test_an_email_that_is_not_text_is_never_merged():
    rows = [{"email": None}, {"email": None}]
    assert len(dedupe(rows)) == 2


def test_an_empty_input_returns_an_empty_list():
    assert dedupe([]) == []
