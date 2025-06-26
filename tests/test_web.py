#!/usr/bin/env python3
"""
測試網站應用的基本功能
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app.main import app

client = TestClient(app)

def test_home_page():
    """測試首頁"""
    response = client.get("/")
    assert response.status_code == 200
    assert "旅行支出分帳系統" in response.text

def test_register_page():
    """測試註冊頁面"""
    response = client.get("/register")
    assert response.status_code == 200
    assert "註冊新帳號" in response.text

def test_login_page():
    """測試登入頁面"""
    response = client.get("/login")
    assert response.status_code == 200
    assert "登入" in response.text

def test_user_registration():
    """測試用戶註冊"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    response = client.post("/api/register", json=user_data)
    assert response.status_code == 200
    assert "註冊成功" in response.json()["message"]

def test_user_login():
    """測試用戶登入"""
    # 先註冊一個用戶
    user_data = {
        "username": "logintest",
        "email": "logintest@example.com", 
        "password": "testpass123"
    }
    client.post("/api/register", json=user_data)
    
    # 測試登入
    login_data = {
        "username": "logintest",
        "password": "testpass123"
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_duplicate_registration():
    """測試重複註冊"""
    user_data = {
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "testpass123"
    }
    # 第一次註冊
    response1 = client.post("/api/register", json=user_data)
    assert response1.status_code == 200
    
    # 第二次註冊相同用戶名
    response2 = client.post("/api/register", json=user_data)
    assert response2.status_code == 400
    assert "用戶名已存在" in response2.json()["detail"]

def test_invalid_login():
    """測試無效登入"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpass"
    }
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 401
    assert "用戶名或密碼錯誤" in response.json()["detail"]

if __name__ == "__main__":
    print("開始測試網站應用...")
    
    # 運行測試
    test_functions = [
        test_home_page,
        test_register_page, 
        test_login_page,
        test_user_registration,
        test_user_login,
        test_duplicate_registration,
        test_invalid_login
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__} - 通過")
            passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} - 失敗: {e}")
            failed += 1
    
    print(f"\n測試結果: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("🎉 所有測試通過！應用功能正常。")
    else:
        print("⚠️  部分測試失敗，請檢查應用配置。")