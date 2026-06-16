from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from main import app
from app.models.user import User, OTPLog
from app.utils.security import hash_password, hash_otp, create_access_token

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    user = User(
        phone="+254700000000",
        email="test@example.com",
        name="Test User",
        password=hash_password("password123"),
        role="seller",
        verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id), "role": test_user.role.value})
    return {"Authorization": f"Bearer {token}"}


class TestRegister:
    def test_register_creates_user(self, db):
        res = client.post("/api/v1/auth/register", json={
            "phone": "+254711111111",
            "email": "new@example.com",
            "name": "New User",
            "password": "password123",
            "role": "seller",
        })
        assert res.status_code == 201
        assert res.json()["phone"] == "+254711111111"

        user = db.query(User).filter(User.phone == "+254711111111").first()
        assert user is not None
        assert user.role.value == "seller"

    def test_register_duplicate_phone_fails(self, test_user):
        res = client.post("/api/v1/auth/register", json={
            "phone": test_user.phone,
            "email": "another@example.com",
            "name": "Duplicate",
            "password": "password123",
            "role": "recycler",
        })
        assert res.status_code == 409

    def test_register_duplicate_email_fails(self, test_user):
        res = client.post("/api/v1/auth/register", json={
            "phone": "+254722222222",
            "email": test_user.email,
            "name": "Duplicate",
            "password": "password123",
            "role": "recycler",
        })
        assert res.status_code == 409


class TestOTP:
    def test_send_otp(self, test_user):
        res = client.post("/api/v1/auth/send-otp", json={"phone": test_user.phone})
        assert res.status_code == 200
        assert res.json()["message"] == "OTP sent"

    def test_send_otp_nonexistent_phone(self):
        res = client.post("/api/v1/auth/send-otp", json={"phone": "+254799999999"})
        assert res.status_code == 404

    def test_verify_otp_success(self, db, test_user):
        otp = "123456"
        log = OTPLog(
            phone=test_user.phone,
            otp=hash_otp(otp),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
        )
        db.add(log)
        db.commit()

        res = client.post("/api/v1/auth/verify-otp", json={
            "phone": test_user.phone,
            "otp": otp,
        })
        assert res.status_code == 200
        assert "access_token" in res.json()
        assert "refresh_token" in res.json()

    def test_verify_otp_expired_fails(self, db, test_user):
        otp = "654321"
        log = OTPLog(
            phone=test_user.phone,
            otp=hash_otp(otp),
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
        )
        db.add(log)
        db.commit()

        res = client.post("/api/v1/auth/verify-otp", json={
            "phone": test_user.phone,
            "otp": otp,
        })
        assert res.status_code == 400

    def test_verify_otp_invalid_code(self, test_user):
        res = client.post("/api/v1/auth/verify-otp", json={
            "phone": test_user.phone,
            "otp": "000000",
        })
        assert res.status_code == 400


class TestAuth:
    def test_get_current_user_returns_profile(self, test_user, auth_headers):
        res = client.get("/api/v1/users/me", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["phone"] == test_user.phone
        assert res.json()["role"] == test_user.role.value

    def test_protected_route_without_token(self):
        res = client.get("/api/v1/users/me")
        assert res.status_code == 401

    def test_refresh_token(self, test_user, auth_headers):
        res = client.post("/api/v1/auth/refresh-token", json={
            "token": auth_headers["Authorization"].split(" ")[1]
        })
        assert res.status_code == 200
        assert "access_token" in res.json()


class TestUsers:
    def test_update_profile(self, test_user, auth_headers):
        res = client.put("/api/v1/users/me", headers=auth_headers, json={
            "name": "Updated Name",
            "location": "Nairobi",
        })
        assert res.status_code == 200
        assert res.json()["name"] == "Updated Name"
        assert res.json()["location"] == "Nairobi"

    def test_admin_can_get_user(self, db, auth_headers):
        admin = User(
            phone="+254700000001",
            name="Admin User",
            password=hash_password("admin123"),
            role="admin",
            verified=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        admin_token = create_access_token({"sub": str(admin.id), "role": "admin"})
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        res = client.get(f"/api/v1/users/{admin.id}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["role"] == "admin"

    def test_non_admin_cannot_get_other_user(self, test_user, auth_headers, db):
        other = User(
            phone="+254700000002",
            name="Other User",
            password=hash_password("password123"),
            role="seller",
            verified=True,
        )
        db.add(other)
        db.commit()

        res = client.get(f"/api/v1/users/{other.id}", headers=auth_headers)
        assert res.status_code == 403