"""An account that can be withdrawn from."""


class Account:
    def __init__(self, balance=0):
        self._balance = balance
        self._statement = []

    def balance(self):
        return self._balance

    def statement(self):
        return list(self._statement)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("a withdrawal must be positive")
        if amount > self._balance:
            return False
        self._balance -= amount
        self._statement.append(("withdraw", amount))
        return True
