from __future__ import annotations

import copy

import pandas as pd
from loguru import logger
from pydantic import BaseModel
from pydantic import Field

from .balance import Balance
from .currency import Currency
from .payment import Debt
from .payment import Payment
from .rate import query_rate
from .transaction import Transaction
from .utils import read_google_sheet

DEFAULT_CURRENCY = Currency.TWD


class SharePay(BaseModel):
    name: str
    balances: dict[str, Balance] = Field(default_factory=dict)
    currency: Currency = Field(default=DEFAULT_CURRENCY)
    payments: list[Payment] = Field(default_factory=list)
    debts: list[Debt] = Field(default_factory=list)
    alias: dict[str, str] = Field(default_factory=dict)

    def add_payment(self, amount: float, payer: str, members: list[str], currency: Currency | None = None) -> Payment:
        payer = payer.lower().strip()
        members = [name.lower().strip() for name in members]

        self.add_balance(payer)
        for name in members:
            self.add_balance(name)

        if currency is None:
            currency = self.currency

        payment = Payment(amount=amount, currency=currency, payer=payer, members=members)

        self.payments.append(payment)
        self.debts += payment.debts()

        return payment

    def add_balance(self, owner: str) -> None:
        owner = owner.lower().strip()

        if owner in self.balances:
            return

        self.balances[owner] = Balance(owner=owner, currency=self.currency)

    def add_member(self, member: str) -> None:
        """
        Add a new member to the balances if not already present.
        """
        member = member.lower().strip()
        if member not in self.balances:
            self.balances[member] = Balance(owner=member, currency=self.currency)
            logger.info(f"Member {member} added to balances.")
        else:
            logger.info(f"Member {member} already exists in balances.")

    def get_members(self) -> list[str]:
        """
        Get the list of members in the balances.
        """
        return list(self.balances.keys())

    def reset_balance(self) -> None:
        for balance in self.balances.values():
            balance.value = 0

    def calculate_balance(self) -> None:
        for debt in self.debts:
            amount = debt.amount * query_rate(debt.currency, self.currency)

            self.balances[self.alias.get(debt.creditor, debt.creditor)].value -= amount
            self.balances[self.alias.get(debt.debtor, debt.debtor)].value += amount

    def settle_up(self, epsilon: float = 1e-6) -> list[Transaction]:
        self.reset_balance()
        self.calculate_balance()

        transactions = []
        balances = copy.deepcopy(list(self.balances.values()))
        while len(balances) > 1:
            balances = sorted(balances, key=lambda x: x.value)

            recipient = balances[0]
            sender = balances.pop()
            amount = sender.value

            # ignore small amount
            if abs(amount) < epsilon:
                break

            transactions.append(
                Transaction(
                    sender=sender.owner,
                    recipient=recipient.owner,
                    amount=amount,
                    currency=self.currency,
                )
            )
            sender.value -= amount
            recipient.value += amount

        for t in transactions:
            logger.info(t)

        return transactions

    def delete_payment(self, payment_id: str) -> bool:
        """
        Delete a payment by its id.
        """
        for i, payment in enumerate(self.payments):
            if payment.id == payment_id:
                del self.payments[i]
                self.debts = [debt for debt in self.debts if debt not in payment.debts()]
                logger.info(f"Payment with id {payment_id} deleted.")
                return True
        logger.info(f"Payment with id {payment_id} not found.")
        return False

    @classmethod
    def from_df(cls, df: pd.DataFrame, alias: dict | None = None, currency: Currency | None = None) -> SharePay:
        project = cls(name="df", alias=alias or {}, currency=currency or DEFAULT_CURRENCY)
        for _, row in df.iterrows():
            if row.isna().any():
                logger.debug("NaN value found: {}, skip", row.to_dict())
                continue

            project.add_payment(
                amount=row["amount"],
                payer=row["payer"].lower().strip(),
                members=row["members"].replace(" ", "").lower().split(","),
                currency=row["currency"].upper(),
            )
        return project

    @classmethod
    def from_sheet(cls, url: str, alias: dict | None = None, currency: Currency | None = None) -> SharePay:
        df = read_google_sheet(url)
        return cls.from_df(df, alias=alias or {}, currency=currency or DEFAULT_CURRENCY)
