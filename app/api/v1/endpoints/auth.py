from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schemas import (
    RegisterRequest,
    SendOTPRequest,
    VerifyOTPRequest,
    TokenResponse,
    RefreshTokenRequest,
)
from app.services.auth_service import register_user, send_otp, verify_otp, authenticate_with_otp, refresh_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    try:
        register_user(db, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    otp = send_otp(db, data.phone)
    return {"message": "Registration successful. OTP sent.", "phone": data.phone}


@router.post("/send-otp", status_code=status.HTTP_200_OK)
def request_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        authenticate_with_otp(db, data.phone)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return {"message": "OTP sent", "phone": data.phone}


@router.post("/verify-otp", response_model=TokenResponse)
def verify_otp_endpoint(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        tokens = verify_otp(db, data.phone, data.otp)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/refresh-token")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        tokens = refresh_access_token(db, data.token)
        return tokens
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout():
    return {"message": "Logged out"}