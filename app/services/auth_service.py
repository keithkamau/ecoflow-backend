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


def send_otp(db: Session, phone: str) -> str:
    otp = generate_otp()

    import os
    if os.getenv("ENVIRONMENT", "development") == "development":
        print(f"\n[DEV OTP] Phone: {phone} | OTP: {otp}\n")

    otp_log = OTPLog(
        phone=phone,
        otp=hash_otp(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db.add(otp_log)
    db.commit()

    return otp


def verify_otp(db: Session, phone: str, otp: str) -> dict:
    otp_logs = (
        db.query(OTPLog)
        .filter(
            OTPLog.phone == phone,
            OTPLog.used == False,
            OTPLog.expires_at > datetime.now(timezone.utc),
        )
        .order_by(OTPLog.id.desc())
        .all()
    )

    if not otp_logs:
        raise ValueError("No valid OTP found. Request a new one.")

    for log in otp_logs:
        log.attempts += 1
        if log.attempts > 3:
            log.used = True
            db.commit()
            raise ValueError("Too many attempts. Request a new OTP.")

        if log.otp == hash_otp(otp):
            log.used = True
            db.commit()

            user = db.query(User).filter(User.phone == phone).first()
            if user:
                user.verified = True
                db.commit()

            access_token = create_access_token({"sub": str(user.id), "role": user.role})
            refresh_token = create_refresh_token({"sub": str(user.id)})
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

    db.commit()
    raise ValueError("Invalid OTP")


def refresh_access_token(db: Session, token: str) -> dict:
    payload = verify_token(token)
    user_id = payload["sub"]

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


def authenticate_with_otp(db: Session, phone: str) -> str:
    user = db.query(User).filter(User.phone == phone).first()
    if not user:
        raise ValueError("No account found with this phone number")

    return send_otp(db, phone)
