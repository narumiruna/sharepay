from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pydantic import field_validator

from .currency import Currency
from .debt import Debt
from .member import Member


class Payment(BaseModel):
    amount: float
    currency: Currency
    payer: Member
    members: list[Member] = Field(default_factory=list)
    time: datetime = Field(default_factory=datetime.now)

    @field_serializer("time")
    def serialize_time(self, v: datetime) -> str:
        return v.isoformat()

    @field_validator("time")
    def validate_time(cls, v) -> datetime:
        if isinstance(v, datetime):
            return v
        elif isinstance(v, str):
            return datetime.fromisoformat(v)
        elif isinstance(v, int):
            return datetime.fromtimestamp(v)
        else:
            raise ValueError(f"invalid time: {v}")

    def add_member(self, member: Member) -> Payment:
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
            debts.append(debt)

        return debts
