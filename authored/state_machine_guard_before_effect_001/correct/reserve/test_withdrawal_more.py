from app.withdrawal import Account


def test_a_new_account_has_an_empty_statement():
    assert Account(10).statement() == []


def test_the_statement_is_a_new_list_each_time():
    account = Account(10)
    assert account.statement() is not account.statement()


def test_two_withdrawals_are_both_recorded():
    account = Account(100)
    account.withdraw(10)
    account.withdraw(20)
    assert len(account.statement()) == 2
