from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.user import User, OTPLog
from app.schemas.user_schemas import RegisterRequest
from app.utils.security import (
    hash_password,
    generate_otp,
    hash_otp,
    create_access_token,
    create_refresh_token,
    verify_token,
)


def register_user(db: Session, data: RegisterRequest) -> User:
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise ValueError("Phone already registered")

    if data.email:
        email_exists = db.query(User).filter(User.email == data.email).first()
        if email_exists:
            raise ValueError("Email already registered")

    user = User(
        phone=data.phone,
        email=data.email,
        name=data.name,
        password=hash_password(data.password),
        role=data.role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password):
        raise ValueError("Invalid email or password")

    if not user.verified:
        raise ValueError("Account not verified")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, token: str) -> dict:
    payload = verify_token(token)
    user_id = payload["sub"]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    access_token = create_access_token({"sub": str(user.id), "role": user.role if isinstance(user.role, str) else user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_with_otp(db: Session, phone: str) -> str:
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise ValueError("No account found with this phone number")

    return send_otp(db, phone)