from app.lease import LeaseTable


def test_a_free_item_can_be_claimed():
    table = LeaseTable(duration=10)
    assert table.claim("job", "w1", now=0) is True


def test_a_live_lease_blocks_another_worker():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.claim("job", "w2", now=3) is False


def test_the_holder_is_reported_while_the_lease_runs():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.holder("job", now=4) == "w1"


def test_an_expired_lease_lets_another_worker_in():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.claim("job", "w2", now=10) is True


def test_the_holder_may_extend_its_own_lease():
    """A worker that checks in early keeps the item; the term restarts from that moment."""
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.claim("job", "w1", now=5) is True
    assert table.is_claimed("job", now=13) is True


def test_release_frees_the_item_at_once():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    table.release("job", "w1")
    assert table.claim("job", "w2", now=1) is True


def test_only_the_holder_may_release():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    assert table.release("job", "w2") is False


def test_an_unknown_item_is_not_claimed():
    assert LeaseTable().is_claimed("nothing", now=0) is False
