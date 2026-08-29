from app.envelope import decode


def test_a_version_two_envelope_with_no_data_is_empty():
    assert decode({"version": 2}) == {}


def test_a_null_body_is_read_as_empty():
    assert decode({"version": 1, "body": None}) == {}


def test_the_body_contents_are_carried_through():
    assert decode({"version": 1, "body": {"x": [1, 2]}})["x"] == [1, 2]
