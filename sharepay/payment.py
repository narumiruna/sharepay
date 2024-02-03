from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field

from .currency import Currency
from .debt import Debt
from .member import Member


class Payment(BaseModel):
    amount: float
    currency: Currency
    payer: Member
    members: list[Member] = Field(default_factory=list)
    time: datetime = Field(default_factory=datetime.now)

    def add_member(self, member) -> Payment:
        self.members.append(member)
        return self

    def debts(self) -> Debt:
        debts = []

        num_members = len(self.members)
        avg_amount = self.amount / num_members
        for m in self.members:
            if m == self.payer:
                continue

            debt = Debt(
                creditor=self.payer,
                debtor=m,
                currency=self.currency,
                amount=avg_amount,
            )
            m.balance -= avg_amount
            self.payer.balance += avg_amount

            debts += [debt]

        return debts
