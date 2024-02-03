from __future__ import annotations

import copy

import pandas as pd
from pydantic import BaseModel
from pydantic import Field

from .currency import Currency
from .member import Member
from .payment import Debt
from .payment import Payment
from .rate import query_rate
from .utils import parse_currency
from .utils import parse_float
from .utils import parse_name
from .utils import parse_names


class Project(BaseModel):
    name: str
    members: dict[str, Member] = Field(default_factory=dict)
    currency: Currency = Field(default=Currency.TWD)
    payments: list[Payment] = Field(default_factory=list)
    debts: list[Debt] = Field(default_factory=list)
    alias: dict[str, str] = Field(default_factory=dict)

    def create_payment(
        self, amount: float, payer_name: str, member_names: list[str], currency: str | None = None
    ) -> Payment:
        self.add_member(payer_name)
        for name in member_names:
            self.add_member(name)

        if currency is None:
            currency = self.currency

        p = Payment(
            amount=amount,
            currency=currency,
            payer=self.members[payer_name],
            members=[self.members[name] for name in member_names],
        )

        self.payments.append(p)
        self.debts += p.debts()

    def add_member(self, name: str) -> None:
        if name in self.members:
            return

        m = Member(name=name)
        self.members[name] = m

    def reset_balance(self) -> None:
        for m in self.members.values():
            m.balance = 0

    def get_alias(self, member: Member) -> Member:
        if member.name in self.alias:
            return self.members[self.alias[member.name]]
        return member

    def cal_balance(self) -> None:
        for d in self.debts:
            amount = d.amount
            if d.currency != self.currency:
                rate = query_rate(d.currency, self.currency)
                amount *= rate

            self.get_alias(d.creditor).balance += amount
            self.get_alias(d.debtor).balance -= amount

    def settle_up(self) -> None:
        self.reset_balance()
        self.cal_balance()

        members = copy.deepcopy(list(self.members.values()))
        while len(members) > 1:
            members = sorted(members, key=lambda x: -x.balance)

            richest = members[0]
            poorest = members.pop()
            amount = poorest.balance

            print(f"{poorest.name: <6} -> {richest.name: <6} {-amount: >10.2f}")
            richest.balance += amount

    @classmethod
    def from_df(cls, df: pd.DataFrame, alias: dict | None = None) -> Project:
        project = cls(name="df", alias=alias or {})
        for _, row in df.iterrows():
            project.create_payment(
                amount=parse_float(row["amount"]),
                payer_name=parse_name(row["payer"]),
                member_names=parse_names(row["members"]),
                currency=parse_currency(row["currency"]),
            )
        return project
