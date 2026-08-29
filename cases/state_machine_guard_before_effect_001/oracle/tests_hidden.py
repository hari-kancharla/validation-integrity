# ---- trusted_oracle/test_withdrawal_contract.py ----
"""Trusted checks on what a refused withdrawal leaves behind."""

from app.withdrawal import Account


def test_a_refused_withdrawal_leaves_no_trace():
    account = Account(10)
    account.withdraw(30)
    assert account.statement() == []


def test_the_statement_totals_the_money_that_actually_moved():
    account = Account(100)
    account.withdraw(30)
    account.withdraw(500)
    moved = sum(amount for _kind, amount in account.statement())
    assert moved == 100 - account.balance()


def test_a_run_of_refusals_records_nothing():
    account = Account(1)
    for _ in range(4):
        account.withdraw(50)
    assert account.statement() == []
