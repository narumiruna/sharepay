from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./travel_expenses.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    created_trips = relationship("Trip", back_populates="creator")
    memberships = relationship("TripMember", back_populates="user")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    currency = Column(String, default="TWD")
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 關聯
    creator = relationship("User", back_populates="created_trips")
    members = relationship("TripMember", back_populates="trip")
    payments = relationship("Payment", back_populates="trip")


class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 允許為空，支持非註冊成員
    guest_name = Column(String, nullable=True)  # 非註冊成員的姓名
    joined_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # 關聯
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="memberships")

    @property
    def display_name(self):
        """返回顯示名稱：註冊用戶返回 username，非註冊用戶返回 guest_name"""
        if self.user:
            return self.user.username
        return self.guest_name


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    payer_trip_member_id = Column(Integer, ForeignKey("trip_members.id"))  # 改為關聯到 TripMember
    amount = Column(Float)
    currency = Column(String)
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯
    trip = relationship("Trip", back_populates="payments")
    payer_trip_member = relationship("TripMember")  # 付款人可以是註冊或非註冊成員
    splits = relationship("PaymentSplit", back_populates="payment")

    @property
    def payer_name(self):
        """返回付款人名稱"""
        if self.payer_trip_member:
            return self.payer_trip_member.display_name
        return "未知"


class PaymentSplit(Base):
    __tablename__ = "payment_splits"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    trip_member_id = Column(Integer, ForeignKey("trip_members.id"))  # 改為關聯到 TripMember
    amount = Column(Float)

    # 關聯
    payment = relationship("Payment", back_populates="splits")
    trip_member = relationship("TripMember")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)
