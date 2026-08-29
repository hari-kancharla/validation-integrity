from app.switchboard import Switchboard


def test_an_empty_table_handles_nothing():
    assert Switchboard({}).handle("anything") is None


def test_the_handlers_result_is_returned():
    assert Switchboard({"e": lambda: 42}).handle("e") == 42


def test_two_events_are_both_counted():
    board = Switchboard({"a": lambda: 1, "b": lambda: 2})
    board.handle("a")
    board.handle("b")
    assert board.handled() == 2
