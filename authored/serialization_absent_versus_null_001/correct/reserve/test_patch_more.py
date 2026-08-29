from app.patch import apply_patch


def test_patching_an_empty_record_adds_everything():
    assert apply_patch({}, {"a": 1}) == {"a": 1}


def test_the_result_is_a_new_object():
    record = {"a": 1}
    assert apply_patch(record, {}) is not record


def test_a_false_value_is_a_real_update():
    assert apply_patch({"flag": True}, {"flag": False}) == {"flag": False}
