# ---- trusted_oracle/test_reader_contract.py ----
"""Trusted checks on a leading byte order mark."""

from app.reader import first_field

BOM = chr(0xFEFF)


def test_a_leading_mark_is_not_part_of_the_field():
    assert first_field(BOM.encode("utf-8") + b"name,age") == "name"


def test_a_marked_document_reads_the_same_as_an_unmarked_one():
    marked = BOM.encode("utf-8") + b"alpha,beta"
    assert first_field(marked) == first_field(b"alpha,beta")


def test_a_mark_before_a_single_field_is_removed():
    assert first_field(BOM.encode("utf-8") + b"solo") == "solo"
