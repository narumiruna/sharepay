from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from sharepay import Currency
from sharepay import SharePay

app = FastAPI()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
DATABASE_URL = "sqlite:///./sharepay.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# CORS settings
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Trip(Base):
    __tablename__ = "trips"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    currency = Column(String)
    alias = Column(String)


class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"))
    amount = Column(Float)
    currency = Column(String)
    payer = Column(String)
    members = Column(String)


Base.metadata.create_all(bind=engine)


# Pydantic models
class CreateUserRequest(BaseModel):
    username: str
    password: str


class CreateTripRequest(BaseModel):
    name: str
    currency: Currency
    alias: dict[str, str] = {}


class AddPaymentRequest(BaseModel):
    trip_name: str
    amount: float
    payer: str
    members: list[str]
    currency: Currency


class AddMemberRequest(BaseModel):
    trip_name: str
    member_name: str


class DeletePaymentRequest(BaseModel):
    trip_name: str
    payment_id: int


# Utility functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(password, user.hashed_password):
        return user
    return None


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register_user(request: CreateUserRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == request.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(request.password)
    db_user = User(username=request.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": user.username, "token_type": "bearer"}


@app.post("/create")
def create_trip(request: CreateTripRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if db.query(Trip).filter(Trip.name == request.name).first():
        raise HTTPException(status_code=400, detail="Trip already exists")
    db_trip = Trip(name=request.name, currency=request.currency, alias=str(request.alias))
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return {"message": "Trip created successfully"}


@app.post("/add_payment")
def add_payment(request: AddPaymentRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == request.trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db_payment = Payment(
        trip_id=trip.id,
        amount=request.amount,
        currency=request.currency,
        payer=request.payer,
        members=",".join(request.members),
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return {"message": "Payment added successfully"}


@app.delete("/delete_payment")
def delete_payment(request: DeletePaymentRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == request.trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    payment = db.query(Payment).filter(Payment.trip_id == trip.id, Payment.id == request.payment_id).first()
    if not payment:
        raise HTTPException(status_code=400, detail="Invalid payment ID")
    db.delete(payment)
    db.commit()
    return {"message": "Payment deleted successfully"}


@app.post("/settle_up")
def settle_up(trip_name: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    payments = db.query(Payment).filter(Payment.trip_id == trip.id).all()
    sharepay = SharePay(name=trip.name, currency=trip.currency, alias=eval(trip.alias))
    for payment in payments:
        sharepay.add_payment(
            amount=payment.amount, payer=payment.payer, members=payment.members.split(","), currency=payment.currency
        )
    transactions = sharepay.settle_up()
    return {"transactions": transactions}


@app.post("/add_member")
def add_member(request: AddMemberRequest, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == request.trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    sharepay = SharePay(name=trip.name, currency=trip.currency, alias=eval(trip.alias))
    sharepay.add_balance(request.member_name)
    return {"message": "Member added successfully"}


@app.get("/members")
def get_members(trip_name: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    payments = db.query(Payment).filter(Payment.trip_id == trip.id).all()
    sharepay = SharePay(name=trip.name, currency=trip.currency, alias=eval(trip.alias))
    for payment in payments:
        sharepay.add_payment(
            amount=payment.amount, payer=payment.payer, members=payment.members.split(","), currency=payment.currency
        )
    return list(sharepay.balances.keys())


@app.get("/trips")
def get_trips(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trips = db.query(Trip).all()
    return [trip.name for trip in trips]


@app.get("/payments")
def get_payments(trip_name: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    trip = db.query(Trip).filter(Trip.name == trip_name).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    payments = db.query(Payment).filter(Payment.trip_id == trip.id).all()
    return [
        {
            "amount": payment.amount,
            "currency": payment.currency,
            "payer": payment.payer,
            "members": payment.members.split(","),
        }
        for payment in payments
    ]


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/app.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)


@app.get("/login", response_class=HTMLResponse)
def read_login():
    with open("templates/login.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)


@app.get("/register", response_class=HTMLResponse)
def read_register():
    with open("templates/register.html", "r") as file:
        return HTMLResponse(content=file.read(), status_code=200)
