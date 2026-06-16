from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services.auth_service import register_user, login_user, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, data)
        return {"message": "Registration successful", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    try:
        tokens = login_user(db, data.email, data.password)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh-token")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        tokens = refresh_access_token(db, data.token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
