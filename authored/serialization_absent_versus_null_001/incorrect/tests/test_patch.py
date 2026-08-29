from app.patch import apply_patch


def test_a_named_field_is_replaced():
    assert apply_patch({"a": 1}, {"a": 2}) == {"a": 2}


def test_an_unmentioned_field_is_left_alone():
    assert apply_patch({"a": 1, "b": 2}, {"a": 9})["b"] == 2


def test_a_new_field_is_added():
    assert apply_patch({"a": 1}, {"b": 2}) == {"a": 1, "b": 2}


def test_the_input_record_is_not_modified():
    record = {"a": 1}
    apply_patch(record, {"a": 2})
    assert record == {"a": 1}


def test_an_empty_patch_changes_nothing():
    assert apply_patch({"a": 1}, {}) == {"a": 1}


def test_an_empty_value_is_not_an_update():
    """Clients send empty fields for anything they did not fill in, so those are skipped."""
    assert apply_patch({"a": 1}, {"a": None}) == {"a": 1}


def test_several_fields_are_patched_at_once():
    assert apply_patch({"a": 1, "b": 2}, {"a": 3, "b": 4}) == {"a": 3, "b": 4}
