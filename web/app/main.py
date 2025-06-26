from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import sys
import os

# 添加父目錄到路徑，以便導入sharepay模塊
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# 導入應用模塊
from app.database import get_db, create_tables, User, Trip, TripMember, Payment, PaymentSplit
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas import UserCreate, UserLogin, Token, TripCreate, PaymentCreate, BalanceInfo, SettlementTransaction

# 導入SharePay核心模塊
from src.sharepay.sharepay import SharePay
from src.sharepay.currency import Currency

app = FastAPI(title="旅行支出分帳系統")

# 靜態文件和模板
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

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
async def login(user: UserLogin, db: Session = Depends(get_db)):
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
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    try:
        from app.auth import get_current_user
        from fastapi.security import HTTPAuthorizationCredentials
        
        # 嘗試從Authorization header獲取token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            credentials = HTTPAuthorizationCredentials(scheme='Bearer', credentials=auth_header[7:])
            return get_current_user(credentials, db)
    except:
        pass
    return None


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {
        "request": request
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
async def create_trip(trip: TripCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
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
async def trip_detail(trip_id: int, request: Request, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
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