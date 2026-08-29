# ---- reserve/test_importer_more.py ----
from app.importer import Lock, import_batch


def test_a_new_lock_is_free():
    assert Lock().held is False


def test_a_single_row_batch_imports_one():
    assert import_batch(Lock(), [{"a": 1}]) == 1


def test_the_count_is_a_whole_number():
    assert isinstance(import_batch(Lock(), []), int)
