from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user_schemas import RegisterRequest
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token


def register_user(db: Session, data: RegisterRequest) -> User:
    if db.query(User).filter(User.phone == data.phone).first():
        raise ValueError("Phone already registered")
    if data.email and db.query(User).filter(User.email == data.email).first():
        raise ValueError("Email already registered")

    user = User(
        phone=data.phone,
        email=data.email,
        name=data.name,
        password=hash_password(data.password),
        role=data.role.value,
        verified=True,
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(user)
    return user


def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.password):
        raise ValueError("Invalid email or password")

    return {
        "access_token": create_access_token({"sub": str(user.id), "role": user.role}),
        "refresh_token": create_refresh_token({"sub": str(user.id)}),
        "token_type": "bearer",
    }


def refresh_access_token(db: Session, token: str) -> dict:
    payload = verify_token(token)
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise ValueError("User not found")

    return {
        "access_token": create_access_token({"sub": str(user.id), "role": user.role if isinstance(user.role, str) else user.role.value}),
        "token_type": "bearer",
    }