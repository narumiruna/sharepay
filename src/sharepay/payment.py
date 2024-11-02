from __future__ import annotations

from datetime import datetime

import dateutil.parser
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pydantic import field_validator

from .currency import Currency
from .debt import Debt


class Payment(BaseModel):
    amount: float
    currency: Currency
    payer: str
    members: list[str] = Field(default_factory=list)
    time: datetime | str = Field(default_factory=datetime.now)

    @field_serializer("time")
    def serialize_time(self, v: datetime) -> str:
        return v.isoformat()

    @field_validator("time", mode="before")
    @classmethod
    def parse_time(cls, v: datetime | str) -> datetime:
        if isinstance(v, str):
            return dateutil.parser.parse(v)

        return v

    def debts(self) -> list[Debt]:
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
