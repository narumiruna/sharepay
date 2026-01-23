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

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from sharepay_web.database import Base  # noqa: E402
from sharepay_web.database import get_db  # noqa: E402
from sharepay_web.main import app  # noqa: E402

# Use a test database
TEST_DATABASE_URL = "sqlite:///./test_travel_expenses.db"


@pytest.fixture(scope="function")
def test_db():
    """Create an isolated database for each test."""
    # Create the test engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = testing_session_local()
            yield db
        finally:
            db.close()

    # Override dependency
    app.dependency_overrides[get_db] = override_get_db

    yield testing_session_local

    # Cleanup after the test
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    app.dependency_overrides.clear()

    # Remove the test database file
    if os.path.exists("test_travel_expenses.db"):
        os.remove("test_travel_expenses.db")


@pytest.fixture(scope="function")
def client(test_db):
    """Test client."""
    with TestClient(app) as test_client:
        yield test_client


def test_home_page(client) -> None:
    """Test the home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert "旅行支出分帳系統" in response.text


def test_register_page(client) -> None:
    """Test the registration page."""
    response = client.get("/register")
    assert response.status_code == 200
    assert "註冊新帳號" in response.text


def test_login_page(client) -> None:
    """Test the login page."""
    response = client.get("/login")
    assert response.status_code == 200
    assert "登入" in response.text


def test_user_registration(client) -> None:
    """Test user registration."""
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpass123"}
    response = client.post("/api/register", json=user_data)
    assert response.status_code == 200
    assert "註冊成功" in response.json()["message"]


def test_user_login(client) -> None:
    """Test user login."""
    # Register a user first
    user_data = {"username": "logintest", "email": "logintest@example.com", "password": "testpass123"}
    client.post("/api/register", json=user_data)

    # Test login
    login_data = {"username": "logintest", "password": "testpass123"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_duplicate_registration(client) -> None:
    """Test duplicate registration."""
    user_data = {"username": "duplicate", "email": "duplicate@example.com", "password": "testpass123"}
    # First registration
    response1 = client.post("/api/register", json=user_data)
    assert response1.status_code == 200

    # Second registration with the same username
    response2 = client.post("/api/register", json=user_data)
    assert response2.status_code == 400
    assert "用戶名已存在" in response2.json()["detail"]


def test_invalid_login(client) -> None:
    """Test invalid login."""
    login_data = {"username": "nonexistent", "password": "wrongpass"}
    response = client.post("/api/login", json=login_data)
    assert response.status_code == 401
    assert "用戶名或密碼錯誤" in response.json()["detail"]
