from app.importer import Lock, import_batch


def test_an_empty_batch_imports_nothing():
    assert import_batch(Lock(), []) == 0


def test_every_row_is_counted():
    assert import_batch(Lock(), [{"a": 1}, {"b": 2}]) == 2


def test_the_lock_is_taken():
    lock = Lock()
    import_batch(lock, [{"a": 1}])
    assert lock.takes == 1


def test_the_lock_is_released_after_a_clean_batch():
    lock = Lock()
    import_batch(lock, [{"a": 1}])
    assert lock.held is False


def test_an_empty_batch_releases_the_lock():
    lock = Lock()
    import_batch(lock, [])
    assert lock.held is False


def test_a_bad_row_stops_the_import():
    assert import_batch(Lock(), [{"a": 1}, "not a row", {"b": 2}]) == 1
