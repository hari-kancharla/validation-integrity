"""Trusted checks for which row survives a duplicate group."""

from app.dedupe import dedupe


def test_the_first_occurrence_survives_untouched():
    rows = [
        {"email": "  Ada@Example.COM ", "name": "Ada", "note": "first"},
        {"email": "ada@example.com", "name": "Ada Lovelace", "note": "second"},
        {"email": "ADA@EXAMPLE.COM", "name": "A. L.", "note": "third"},
    ]
    result = dedupe(rows)
    assert len(result) == 1
    assert result[0] is rows[0]
    assert result[0] == {"email": "  Ada@Example.COM ", "name": "Ada", "note": "first"}


def test_the_first_occurrence_survives_in_a_longer_sheet():
    rows = [
        {"email": "ada@example.com", "name": "First"},
        {"email": "grace@example.com", "name": "Grace"},
        {"email": " ADA@example.com", "name": "Later"},
    ]
    result = dedupe(rows)
    assert [row["name"] for row in result] == ["First", "Grace"]


def test_unmergeable_rows_are_all_carried_through():
    rows = [{"email": ""}, {"name": "no address"}, {"email": None}, {"email": "  "}]
    assert len(dedupe(rows)) == 4
