from app.wire import to_wire


def test_an_unset_field_is_dropped():
    assert to_wire({"a": 1, "b": None}) == {"a": 1}


def test_a_set_field_is_carried_through():
    assert to_wire({"a": "x"}) == {"a": "x"}


def test_the_input_record_is_not_modified():
    record = {"a": None}
    to_wire(record)
    assert record == {"a": None}


def test_an_empty_record_stays_empty():
    assert to_wire({}) == {}


def test_a_nested_value_is_carried_through_as_it_stands():
    tags = ["x"]
    assert to_wire({"tags": tags})["tags"] is tags


def test_every_set_field_survives():
    assert to_wire({"a": 1, "b": 2, "c": None}) == {"a": 1, "b": 2}


def test_an_empty_list_is_dropped_like_an_unset_field():
    """An empty collection carries nothing, so it is left off the wire."""
    assert to_wire({"tags": []}) == {}
