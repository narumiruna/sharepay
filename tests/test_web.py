#!/usr/bin/env python3
"""
測試網站應用的基本功能
"""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sharepay_web.database import Base  # noqa: E402
from sharepay_web.database import get_db  # noqa: E402
from sharepay_web.main import app  # noqa: E402

# 使用測試資料庫
TEST_DATABASE_URL = "sqlite:///./test_travel_expenses.db"


@pytest.fixture(scope="function")
def test_db():
    """為每個測試創建獨立的資料庫"""
    # 創建測試引擎
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # 創建所有表
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    # 覆蓋依賴
    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal

    # 測試結束後清理
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

    # 刪除測試資料庫文件
    if os.path.exists("test_travel_expenses.db"):
        os.remove("test_travel_expenses.db")


@pytest.fixture(scope="function")
def client(test_db):
    """測試客戶端"""
    return TestClient(app)


def test_home_page(client):
    """測試首頁"""
    response = client.get("/")
    assert response.status_code == 200
    assert "旅行支出分帳系統" in response.text


def test_register_page(client):
    """測試註冊頁面"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "註冊新帳號" in response.text


def test_login_page(client):
    """測試登入頁面"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "登入" in response.text


def test_user_registration(client):
    """測試用戶註冊"""
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpass123"}
    response = client.post("/api/register", json=user_data)
    assert response.status_code == 200
    assert "註冊成功" in response.json()["message"]


def test_user_login(client):
    """測試用戶登入"""
    # 先註冊一個用戶
    user_data = {"username": "logintest", "email": "logintest@example.com", "password": "testpass123"}
    client.post("/api/register", json=user_data)

    # 測試登入
    login_data = {"username": "logintest", "password": "testpass123"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_duplicate_registration(client):
    """測試重複註冊"""
    user_data = {"username": "duplicate", "email": "duplicate@example.com", "password": "testpass123"}
    # 第一次註冊
    response1 = client.post("/api/register", json=user_data)
    assert response1.status_code == 200

    # 第二次註冊相同用戶名
    response2 = client.post("/api/register", json=user_data)
    assert response2.status_code == 400
    assert "用戶名已存在" in response2.json()["detail"]


def test_invalid_login(client):
    """測試無效登入"""
    login_data = {"username": "nonexistent", "password": "wrongpass"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 401
    assert "用戶名或密碼錯誤" in response.json()["detail"]
