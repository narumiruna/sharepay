from __future__ import annotations

import copy

from pydantic import BaseModel
from pydantic import Field

from .currency import Currency
from .member import Member
from .payment import Debt
from .payment import Payment
from .rate import query_rate


class Project(BaseModel):
    name: str
    members: list[Member]
    currency: Currency = Field(default=Currency.TWD)
    payments: list[Payment] = Field(default=[])
    debts: list[Debt] = Field(default=[])

    def add_payment(self, payment: Payment) -> Project:
        self.payments.append(payment)
        self.debts += payment.debts()

    def reset_balance(self) -> None:
        for m in self.members:
            m.balance = 0

    def cal_balance(self) -> None:
        for d in self.debts:
            amount = d.amount
            if d.currency != self.currency:
                rate = query_rate(d.currency, self.currency)
                amount *= rate

            d.creditor.balance += amount
            d.debtor.balance -= amount

    def settle_up(self) -> None:
        self.reset_balance()
        self.cal_balance()

        members = copy.deepcopy(self.members)
        while len(members) > 1:
            members = sorted(members, key=lambda x: -x.balance)

            richest = members[0]
            poorest = members.pop()
            amount = poorest.balance

            print(f"{poorest.name: <6} -> {richest.name: <6} {-amount: >10.2f}")
            richest.balance += amount