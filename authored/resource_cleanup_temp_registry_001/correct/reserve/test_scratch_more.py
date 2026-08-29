from app.scratch import Scratch


def test_a_new_register_has_removed_nothing():
    assert Scratch().removed() == []


def test_the_pending_list_is_a_new_list_each_time():
    scratch = Scratch()
    assert scratch.pending() is not scratch.pending()


def test_cleanup_on_an_empty_register_removes_nothing():
    scratch = Scratch()
    scratch.cleanup()
    assert scratch.removed() == []
