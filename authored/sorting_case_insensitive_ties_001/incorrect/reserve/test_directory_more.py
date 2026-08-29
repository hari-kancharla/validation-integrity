from app.directory import listing


def test_the_result_is_a_new_list():
    names = ["a"]
    assert listing(names) is not names


def test_a_single_name_lists_alone():
    assert listing(["solo"]) == ["solo"]


def test_an_empty_name_sorts_first():
    assert listing(["a", ""]) == ["", "a"]
