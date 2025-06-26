import os
from datetime import timedelta

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from sharepay.currency import Currency

# 導入SharePay核心模塊
from sharepay.sharepay import SharePay
from sharepay_web.auth import ACCESS_TOKEN_EXPIRE_MINUTES
from sharepay_web.auth import authenticate_user
from sharepay_web.auth import create_access_token
from sharepay_web.auth import get_current_active_user
from sharepay_web.auth import get_password_hash
from sharepay_web.database import Payment
from sharepay_web.database import PaymentSplit
from sharepay_web.database import Trip
from sharepay_web.database import TripMember
from sharepay_web.database import User
from sharepay_web.database import create_tables

# 導入應用模塊
from sharepay_web.database import get_db
from sharepay_web.schemas import PaymentCreate
from sharepay_web.schemas import SettlementTransaction
from sharepay_web.schemas import Token
from sharepay_web.schemas import TripCreate
from sharepay_web.schemas import UserCreate
from sharepay_web.schemas import UserLogin

app = FastAPI(title="旅行支出分帳系統")

# 靜態文件和模板
static_dir = os.path.join(os.path.dirname(__file__), "static")
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# 創建資料庫表
create_tables()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查用戶是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用戶名已存在")

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email已存在")

    # 創建新用戶
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "註冊成功"}


@app.post("/api/login", response_model=Token)
async def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="用戶名或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": authenticated_user.username}, expires_delta=access_token_expires
    )
    
    # 設置 httpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=False,  # 開發環境設為 False，生產環境應該設為 True
        samesite="lax"
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    try:
        from jose import JWTError, jwt
        from sharepay_web.auth import SECRET_KEY, ALGORITHM

        # 嘗試從 cookie 獲取 token
        token = request.cookies.get("access_token")
        
        # 如果 cookie 中沒有，嘗試從 Authorization header 獲取
        if not token:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header[7:]
        
        if not token:
            return None

        # 驗證 token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None

        # 獲取用戶
        user = db.query(User).filter(User.username == username).first()
        return user
        
    except (JWTError, Exception):
        return None


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user_optional(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
        
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "current_user": current_user
    })


@app.get("/api/dashboard")
async def get_dashboard_data(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    # 獲取用戶的旅行
    user_trips = db.query(Trip).filter(Trip.creator_id == current_user.id).all()

    # 獲取用戶參與的旅行
    member_trips = db.query(Trip).join(TripMember).filter(TripMember.user_id == current_user.id).all()

    all_trips = list(set(user_trips + member_trips))

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email
        },
        "trips": [
            {
                "id": trip.id,
                "name": trip.name,
                "description": trip.description,
                "currency": trip.currency,
                "created_at": trip.created_at.isoformat()
            }
            for trip in all_trips
        ]
    }


@app.post("/api/trips")
async def create_trip(
    trip: TripCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_trip = Trip(
        name=trip.name,
        description=trip.description,
        currency=trip.currency,
        creator_id=current_user.id
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)

    # 將創建者加入為成員
    trip_member = TripMember(trip_id=db_trip.id, user_id=current_user.id)
    db.add(trip_member)
    db.commit()

    return {"message": "旅行創建成功", "trip_id": db_trip.id}


@app.get("/trip/{trip_id}", response_class=HTMLResponse)
async def trip_detail(
    trip_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # 檢查 token 認證，如果沒有就重定向到登入頁面
    current_user = get_current_user_optional(request, db)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    # 檢查用戶是否有權限查看此旅行
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="旅行不存在")

    is_member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id
    ).first()

    if not is_member and trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="無權限查看此旅行")

    # 獲取旅行成員
    members = db.query(User).join(TripMember).filter(TripMember.trip_id == trip_id).all()

    # 獲取支出記錄
    payments = db.query(Payment).filter(Payment.trip_id == trip_id).all()
    payment_list = []
    for payment in payments:
        payer = db.query(User).filter(User.id == payment.payer_id).first()
        payment_list.append({
            'id': payment.id,
            'amount': payment.amount,
            'currency': payment.currency,
            'description': payment.description,
            'date': payment.date,
            'payer_username': payer.username
        })

    return templates.TemplateResponse("trip_detail.html", {
        "request": request,
        "trip": trip,
        "members": members,
        "payments": payment_list,
        "current_user": current_user
    })


@app.post("/api/trips/{trip_id}/payments")
async def add_payment(
    trip_id: int,
    payment: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 檢查用戶是否是旅行成員
    is_member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="無權限在此旅行中添加支出")

    # 創建支出記錄
    db_payment = Payment(
        trip_id=trip_id,
        payer_id=current_user.id,
        amount=payment.amount,
        currency=payment.currency,
        description=payment.description,
        date=payment.date
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    # 創建分攤記錄
    split_amount = payment.amount / len(payment.split_with)
    for user_id in payment.split_with:
        split = PaymentSplit(
            payment_id=db_payment.id,
            user_id=user_id,
            amount=split_amount
        )
        db.add(split)

    db.commit()
    return {"message": "支出添加成功"}


@app.get("/api/trips/{trip_id}/settlement")
async def get_settlement(
    trip_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 檢查權限
    is_member = db.query(TripMember).filter(
        TripMember.trip_id == trip_id,
        TripMember.user_id == current_user.id
    ).first()

    if not is_member:
        raise HTTPException(status_code=403, detail="無權限查看此旅行的結算")

    # 獲取旅行資訊
    trip = db.query(Trip).filter(Trip.id == trip_id).first()

    # 使用SharePay進行結算計算
    sharepay = SharePay(name=trip.name, currency=Currency(trip.currency))

    # 獲取所有支出並添加到SharePay中
    payments = db.query(Payment).filter(Payment.trip_id == trip_id).all()

    for payment in payments:
        payer = db.query(User).filter(User.id == payment.payer_id).first()
        splits = db.query(PaymentSplit).filter(PaymentSplit.payment_id == payment.id).all()

        split_members = []
        for split in splits:
            member = db.query(User).filter(User.id == split.user_id).first()
            split_members.append(member.username)

        sharepay.add_payment(
            amount=payment.amount,
            payer=payer.username,
            members=split_members,
            currency=Currency(payment.currency)
        )

    # 執行結算
    transactions = sharepay.settle_up()

    settlement_transactions = [
        SettlementTransaction(
            from_user=t.sender,
            to_user=t.recipient,
            amount=t.amount,
            currency=t.currency.value
        )
        for t in transactions
    ]

    return {"transactions": settlement_transactions}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

