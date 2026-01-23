import os
from datetime import UTC
from datetime import timedelta
from typing import Any

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from sharepay.currency import Currency

# Import SharePay core module
from sharepay.sharepay import SharePay
from sharepay_web.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from sharepay_web.auth import authenticate_user
from sharepay_web.auth import create_access_token
from sharepay_web.auth import create_refresh_token
from sharepay_web.auth import get_current_active_user
from sharepay_web.auth import get_password_hash
from sharepay_web.auth import verify_refresh_token
from sharepay_web.database import Payment
from sharepay_web.database import PaymentSplit
from sharepay_web.database import Trip
from sharepay_web.database import TripMember
from sharepay_web.database import User
from sharepay_web.database import create_tables

# Import app modules
from sharepay_web.database import get_db
from sharepay_web.schemas import PaymentCreate
from sharepay_web.schemas import SettlementTransaction
from sharepay_web.schemas import Token
from sharepay_web.schemas import TripCreate
from sharepay_web.schemas import UserCreate
from sharepay_web.schemas import UserLogin

app = FastAPI(title="旅行支出分帳系統")

# Static files and templates
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Create database tables
create_tables()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> Response:
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request) -> Response:
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request) -> Response:
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)) -> dict[str, str]:
    # Check whether the user already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用戶名已存在")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email已存在")

    # Create a new user
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "註冊成功"}


@app.post("/api/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user or isinstance(authenticated_user, bool):
        raise HTTPException(
            status_code=401,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(authenticated_user.username)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(authenticated_user.username)})

    # Set the httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # 7 days
        httponly=True,
        secure=False,  # False for development, True for production
        samesite="lax",
    )

    # Set the refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=30 * 24 * 60 * 60,  # 30 days
        httponly=True,
        secure=False,  # False for development, True for production
        samesite="lax",
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.post("/api/refresh", response_model=Token)
async def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, str]:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = verify_refresh_token(refresh_token)
    if not username:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == username).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    # Update the access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/logout")
async def logout(response: Response) -> dict[str, str]:
    # Clear cookies
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "登出成功"}


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    try:
        from jose import JWTError
        from jose import jwt

        from sharepay_web.auth import ALGORITHM
        from sharepay_web.auth import SECRET_KEY

        # Try to get the token from cookies
        token = request.cookies.get("access_token")

        # If not in cookies, try the Authorization header
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]

        if not token:
            return None

        # Validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        # Fetch user
        return db.query(User).filter(User.username == username).first()

    except JWTError:
        return None


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)) -> Response:
    current_user = get_current_user_optional(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("dashboard.html", {"request": request, "current_user": current_user})


@app.get("/api/dashboard")
async def get_dashboard_data(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> dict[str, object]:
    # Fetch trips created by the user
    user_trips = db.query(Trip).filter(Trip.creator_id == current_user.id).all()

    # Fetch trips the user participates in
    member_trips = db.query(Trip).join(TripMember).filter(TripMember.user_id == current_user.id).all()

    all_trips = list(set(user_trips + member_trips))

    return {
        "user": {"id": current_user.id, "username": current_user.username, "email": current_user.email},
        "trips": [
            {
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "currency": trip.currency,
                "created_at": trip.created_at.isoformat(),
            }
            for trip in all_trips
        ],
    }


@app.post("/api/trips")
async def create_trip(
    trip: TripCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> dict[str, object]:
    db_trip = Trip(name=trip.name, description=trip.description, currency=trip.currency, creator_id=current_user.id)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    # Add the creator as a member
    trip_member = TripMember(trip_id=db_trip.id, user_id=current_user.id)
    db.add(trip_member)
    db.commit()

    return {"message": "旅行創建成功", "trip_id": db_trip.id}


@app.get("/trip/{trip_id}", response_class=HTMLResponse)
async def trip_detail(trip_id: int, request: Request, db: Session = Depends(get_db)) -> Response:
    # Check token auth and redirect to login if missing
    current_user = get_current_user_optional(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # Check user permission to view this trip
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="旅行不存在")

    is_member = (
        db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id).first()
    )

    if not is_member and (not trip or trip.creator_id != current_user.id):
        raise HTTPException(status_code=403, detail="無權限查看此旅行")

    # Fetch trip members (registered users and guests)
    trip_members = db.query(TripMember).filter(TripMember.trip_id == trip_id).all()

    # Build member list with display name and ID
    members = []
    for tm in trip_members:
        member_info = {
            "id": tm.id,
            "name": tm.display_name,
            "is_registered": tm.user_id is not None,
            "user_id": tm.user_id,
        }
        members.append(member_info)

    # Fetch payments
    payments = db.query(Payment).filter(Payment.trip_id == trip_id).all()
    payment_list = [
        {
            "id": payment.id,
            "amount": payment.amount,
            "currency": payment.currency,
            "description": payment.description,
            "date": payment.date,
            "payer_username": payment.payer_name,
        }
        for payment in payments
    ]

    return templates.TemplateResponse(
        "trip_detail.html",
        {"request": request, "trip": trip, "members": members, "payments": payment_list, "current_user": current_user},
    )


@app.post("/api/trips/{trip_id}/payments")
async def add_payment(
    trip_id: int,
    payment: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # Check whether the user is a trip member
    is_member = (
        db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id).first()
    )

    if not is_member:
        raise HTTPException(status_code=403, detail="無權限在此旅行中添加支出")

    # Create payment record
    # If payer_trip_member_id is provided, use it; otherwise use the current user's TripMember ID
    payer_trip_member_id = (
        payment.payer_trip_member_id
        if hasattr(payment, "payer_trip_member_id") and payment.payer_trip_member_id
        else None
    )

    if not payer_trip_member_id:
        # Find the current user's TripMember ID in this trip
        current_user_trip_member = (
            db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id).first()
        )
        if current_user_trip_member:
            payer_trip_member_id = int(current_user_trip_member.id)

    db_payment = Payment(
        trip_id=trip_id,
        payer_trip_member_id=payer_trip_member_id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        date=payment.date,
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # Create split records (split_with contains trip_member_id values)
    split_amount = payment.amount / len(payment.split_with)
    for trip_member_id in payment.split_with:
        split = PaymentSplit(payment_id=db_payment.id, trip_member_id=trip_member_id, amount=split_amount)
        db.add(split)

    db.commit()
    return {"message": "支出添加成功"}


@app.get("/api/trips/{trip_id}/settlement")
async def get_settlement(
    trip_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> dict[str, list[SettlementTransaction]]:
    # Check permissions
    is_member = (
        db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id).first()
    )

    if not is_member:
        raise HTTPException(status_code=403, detail="無權限查看此旅行的結算")

    # Fetch trip info
    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    # Use SharePay to compute settlements
    if not trip:
        raise HTTPException(status_code=404, detail="旅行不存在")
    sharepay = SharePay(name=str(trip.name), currency=Currency(str(trip.currency)))

    # Fetch all payments and add them to SharePay
    payments = db.query(Payment).filter(Payment.trip_id == trip_id).all()

    for payment in payments:
        splits = db.query(PaymentSplit).filter(PaymentSplit.payment_id == payment.id).all()

        split_members = []
        for split in splits:
            trip_member = db.query(TripMember).filter(TripMember.id == split.trip_member_id).first()
            if trip_member:
                split_members.append(trip_member.display_name)

        sharepay.add_payment(
            amount=float(payment.amount),
            payer=payment.payer_name,
            members=split_members,
            currency=Currency(str(payment.currency)),
        )

    # Run settlement
    transactions = sharepay.settle_up()

    settlement_transactions = [
        SettlementTransaction(from_user=t.sender, to_user=t.recipient, amount=t.amount, currency=t.currency.value)
        for t in transactions
    ]

    return {"transactions": settlement_transactions}


@app.post("/api/trips/{trip_id}/members")
async def add_trip_member(
    trip_id: int,
    member_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # Check permission (must be trip creator or member)
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="旅行不存在")

    is_member = (
        db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == current_user.id).first()
    )

    if not is_member and (not trip or trip.creator_id != current_user.id):
        raise HTTPException(status_code=403, detail="無權限添加成員到此旅行")

    name = member_data.get("name", "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="請提供成員姓名")

    # Try to find a registered user
    user_to_add = db.query(User).filter(User.username == name).first()

    if user_to_add:
        # Registered user - check if already a member
        existing_member = (
            db.query(TripMember).filter(TripMember.trip_id == trip_id, TripMember.user_id == user_to_add.id).first()
        )

        if existing_member:
            raise HTTPException(status_code=400, detail="用戶已經是旅行成員")

        # Add registered user
        new_member = TripMember(trip_id=trip_id, user_id=user_to_add.id)
    else:
        # Guest user - check if the guest already exists
        existing_guest = (
            db.query(TripMember)
            .filter(TripMember.trip_id == trip_id, TripMember.guest_name == name, TripMember.user_id.is_(None))
            .first()
        )

        if existing_guest:
            raise HTTPException(status_code=400, detail="該名稱的成員已存在")

        # Add guest member
        new_member = TripMember(trip_id=trip_id, guest_name=name)

    db.add(new_member)
    db.commit()

    member_type = "註冊用戶" if user_to_add else "非註冊成員"
    return {"message": f"成員添加成功({member_type})", "name": name}


@app.get("/api/payments/{payment_id}")
async def get_payment(
    payment_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
) -> dict[str, Any]:
    # Fetch payment record
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="支出記錄不存在")

    # Check permission (must be a trip member)
    is_member = (
        db.query(TripMember)
        .filter(TripMember.trip_id == payment.trip_id, TripMember.user_id == current_user.id)
        .first()
    )

    trip = db.query(Trip).filter(Trip.id == payment.trip_id).first()
    if not is_member and (not trip or trip.creator_id != current_user.id):
        raise HTTPException(status_code=403, detail="無權限查看此支出記錄")

    # Fetch split records
    splits = db.query(PaymentSplit).filter(PaymentSplit.payment_id == payment_id).all()
    split_member_ids = [split.trip_member_id for split in splits]

    return {
        "id": payment.id,
        "amount": payment.amount,
        "currency": payment.currency,
        "description": payment.description,
        "date": payment.date.strftime("%Y-%m-%d") if payment.date else None,
        "payer_trip_member_id": payment.payer_trip_member_id,
        "split_with": split_member_ids,
    }


@app.put("/api/payments/{payment_id}")
async def update_payment(
    payment_id: int,
    payment_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    # Fetch payment record
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="支出記錄不存在")

    # Check permission (must be a trip member)
    is_member = (
        db.query(TripMember)
        .filter(TripMember.trip_id == payment.trip_id, TripMember.user_id == current_user.id)
        .first()
    )

    trip = db.query(Trip).filter(Trip.id == payment.trip_id).first()
    if not is_member and (not trip or trip.creator_id != current_user.id):
        raise HTTPException(status_code=403, detail="無權限編輯此支出記錄")

    # Update payment record
    payment.amount = payment_data.get("amount", payment.amount)
    payment.currency = payment_data.get("currency", payment.currency)
    payment.description = payment_data.get("description", payment.description)
    payment.payer_trip_member_id = payment_data.get("payer_trip_member_id", payment.payer_trip_member_id)

    if payment_data.get("date"):
        from datetime import datetime

        payment.date = datetime.strptime(payment_data["date"], "%Y-%m-%d").replace(tzinfo=UTC)

    # Delete old split records
    db.query(PaymentSplit).filter(PaymentSplit.payment_id == payment_id).delete()

    # Create new split records
    split_with = payment_data.get("split_with", [])
    if split_with:
        split_amount = payment.amount / len(split_with)
        for trip_member_id in split_with:
            split = PaymentSplit(payment_id=payment_id, trip_member_id=trip_member_id, amount=split_amount)
            db.add(split)

    db.commit()
    return {"message": "支出記錄更新成功"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
