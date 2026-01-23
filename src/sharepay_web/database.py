from collections.abc import Generator
from datetime import UTC
from datetime import datetime
from typing import cast

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./travel_expenses.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    created_trips = relationship("Trip", back_populates="creator")
    memberships = relationship("TripMember", back_populates="user")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    currency = Column(String, default="TWD")
    creator_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)

    # Relationships
    creator = relationship("User", back_populates="created_trips")
    members = relationship("TripMember", back_populates="trip")
    payments = relationship("Payment", back_populates="trip")


class TripMember(Base):
    __tablename__ = "trip_members"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Allow null for unregistered members
    guest_name = Column(String, nullable=True)  # Name for unregistered members
    joined_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)

    # Relationships
    trip = relationship("Trip", back_populates="members")
    user = relationship("User", back_populates="memberships")

    @property
    def display_name(self) -> str | None:
        """Return display name: username for registered users, guest_name for guests."""
        return cast(str | None, self.user.username if self.user else self.guest_name)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    payer_trip_member_id = Column(Integer, ForeignKey("trip_members.id"))  # Link to TripMember
    amount = Column(Float)
    currency = Column(String)
    description = Column(String)
    date = Column(DateTime, default=lambda: datetime.now(UTC))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Relationships
    trip = relationship("Trip", back_populates="payments")
    payer_trip_member = relationship("TripMember")  # Payer can be registered or guest
    splits = relationship("PaymentSplit", back_populates="payment")

    @property
    def payer_name(self) -> str:
        """Return payer name."""
        if self.payer_trip_member:
            return self.payer_trip_member.display_name
        return "未知"


class PaymentSplit(Base):
    __tablename__ = "payment_splits"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"))
    trip_member_id = Column(Integer, ForeignKey("trip_members.id"))  # Link to TripMember
    amount = Column(Float)

    # Relationships
    payment = relationship("Payment", back_populates="splits")
    trip_member = relationship("TripMember")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
