from datetime import datetime

from pydantic import BaseModel
from pydantic import EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str | None = None


class TripBase(BaseModel):
    name: str
    description: str | None = None
    currency: str = "TWD"


class TripCreate(TripBase):
    pass


class TripMemberInfo(BaseModel):
    id: int
    username: str
    email: str
    joined_at: datetime

    class Config:
        from_attributes = True


class Trip(TripBase):
    id: int
    creator_id: int
    created_at: datetime
    is_active: bool
    members: list[TripMemberInfo] = []

    class Config:
        from_attributes = True


class PaymentBase(BaseModel):
    amount: float
    currency: str
    description: str
    date: datetime | None = None


class PaymentCreate(PaymentBase):
    trip_id: int
    payer_trip_member_id: int | None = None  # 付款人TripMember ID，可選（默認為當前用戶）
    split_with: list[int]  # 與哪些用戶分攤（trip_member_id列表）


class PaymentInfo(BaseModel):
    id: int
    amount: float
    currency: str
    description: str
    date: datetime
    payer_username: str

    class Config:
        from_attributes = True


class Payment(PaymentBase):
    id: int
    trip_id: int
    payer_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceInfo(BaseModel):
    user_id: int
    username: str
    balance: float


class SettlementTransaction(BaseModel):
    from_user: str
    to_user: str
    amount: float
    currency: str
