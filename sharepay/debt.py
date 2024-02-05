from pydantic import BaseModel

from .currency import Currency


class Debt(BaseModel):
    creditor: str
    debtor: str
    currency: Currency
    amount: float
