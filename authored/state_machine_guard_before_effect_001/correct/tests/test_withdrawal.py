import pytest

from app.withdrawal import Account


def test_a_permitted_withdrawal_lowers_the_balance():
    account = Account(100)
    assert account.withdraw(30) is True
    assert account.balance() == 70


def test_a_permitted_withdrawal_is_recorded():
    account = Account(100)
    account.withdraw(30)
    assert account.statement() == [("withdraw", 30)]


def test_a_withdrawal_beyond_the_balance_is_refused():
    account = Account(10)
    assert account.withdraw(30) is False
    assert account.balance() == 10


def test_a_withdrawal_to_exactly_zero_is_permitted():
    account = Account(10)
    assert account.withdraw(10) is True
    assert account.balance() == 0


def test_a_withdrawal_of_zero_is_refused_outright():
    with pytest.raises(ValueError):
        Account(10).withdraw(0)


def test_a_negative_withdrawal_is_refused_outright():
    with pytest.raises(ValueError):
        Account(10).withdraw(-5)
