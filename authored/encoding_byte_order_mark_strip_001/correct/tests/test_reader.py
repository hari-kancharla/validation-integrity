from app.reader import first_field


def test_the_first_field_of_a_plain_line_is_read():
    assert first_field(b"name,age") == "name"


def test_a_line_with_no_comma_is_one_field():
    assert first_field(b"name") == "name"


def test_only_the_first_line_is_read():
    assert first_field(b"first,x" + bytes([10]) + b"second,y") == "first"


def test_a_trailing_carriage_return_is_not_part_of_the_field():
    assert first_field(b"name" + bytes([13, 10]) + b"next") == "name"


def test_an_empty_document_yields_an_empty_field():
    assert first_field(b"") == ""


def test_wide_characters_survive_decoding():
    assert first_field(chr(0x20AC).encode("utf-8") + b",x") == chr(0x20AC)
