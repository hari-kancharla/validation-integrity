from app.wire import to_wire


def test_the_result_is_a_new_mapping():
    record = {"a": 1}
    assert to_wire(record) is not record


def test_a_record_of_only_unset_fields_is_empty():
    assert to_wire({"a": None, "b": None}) == {}


def test_field_names_are_unchanged():
    assert sorted(to_wire({"z": 1, "a": 2})) == ["a", "z"]
