from app.reader import first_field


def test_an_empty_first_field_is_empty():
    assert first_field(b",second") == ""


def test_a_document_of_one_line_feed_yields_nothing():
    assert first_field(bytes([10])) == ""


def test_the_result_is_text():
    assert isinstance(first_field(b"x"), str)
