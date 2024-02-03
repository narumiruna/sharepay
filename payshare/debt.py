from pydantic import BaseModel

from .currency import Currency
from .member import Member


class Debt(BaseModel):
    creditor: Member
    debtor: Member
    currency: Currency
    amount: float
