from app.lease import LeaseTable


def test_releasing_an_unknown_item_reports_failure():
    assert LeaseTable().release("nothing", "w1") is False


def test_two_items_are_leased_separately():
    table = LeaseTable(duration=10)
    table.claim("one", "w1", now=0)
    assert table.claim("two", "w2", now=0) is True


def test_a_released_item_reports_no_holder():
    table = LeaseTable(duration=10)
    table.claim("job", "w1", now=0)
    table.release("job", "w1")
    assert table.holder("job", now=0) is None
