"""Trusted checks on the early exit path."""

from app.importer import Lock, import_batch


def test_a_bad_row_still_releases_the_lock():
    lock = Lock()
    import_batch(lock, ["not a row"])
    assert lock.held is False


def test_the_lock_is_released_exactly_once_on_the_early_path():
    lock = Lock()
    import_batch(lock, [{"a": 1}, "not a row"])
    assert lock.releases == 1


def test_a_run_of_bad_batches_leaves_no_lock_held():
    lock = Lock()
    for _ in range(4):
        import_batch(lock, ["not a row"])
    assert lock.held is False
