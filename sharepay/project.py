from __future__ import annotations

import copy

import pandas as pd
from loguru import logger
from pydantic import BaseModel
from pydantic import Field

from .currency import Currency
from .member import Member
from .payment import Debt
from .payment import Payment
from .rate import query_rate


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
        payer_name = payer_name.lower().strip()
        member_names = [name.lower().strip() for name in member_names]

        self.add_member(payer_name)
        for name in member_names:
            self.add_member(name)

        if currency is None:
            currency = self.currency

        payment = Payment(
            amount=amount,
            currency=currency,
            payer=self.members[payer_name],
            members=[self.members[name] for name in member_names],
        )

        self.payments.append(payment)
        self.debts += payment.debts()

        return payment

    def add_member(self, name: str) -> None:
        name = name.lower().strip()

        if name in self.members:
            return

        self.members[name] = Member(name=name)

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

            print(f"{poorest.name: <6} -> {richest.name: <6} {-amount: >10.2f} {self.currency}")
            richest.balance += amount

    @classmethod
    def from_df(cls, df: pd.DataFrame, alias: dict | None = None, currency: str | None = None) -> Project:
        project = cls(name="df", alias=alias or {}, currency=currency or "TWD")
        for _, row in df.iterrows():
            if row.isna().any():
                logger.debug("NaN value found: {}, skip", row.to_dict())
                continue

            project.create_payment(
                amount=row["amount"],
                payer_name=row["payer"].lower().strip(),
                member_names=row["members"].replace(" ", "").lower().split(","),
                currency=row["currency"].upper(),
            )
        return project
