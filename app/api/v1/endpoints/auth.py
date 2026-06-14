"""Auth endpoints — owned by Member 1."""
from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register():
    return {"detail": "Not implemented — Member 1"}


@router.post("/login")
def login():
    return {"detail": "Not implemented — Member 1"}


@router.post("/verify-otp")
def verify_otp():
    return {"detail": "Not implemented — Member 1"}
