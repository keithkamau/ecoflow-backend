from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ── Enums ──

class UserRole(str, Enum):
    seller = "seller"
    recycler = "recycler"
    admin = "admin"


class KYCStatus(str, Enum):
    none = "none"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class DocStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


# ── Auth ──

class RegisterRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=15, pattern=r"^\+?\d+$")
    email: Optional[EmailStr] = None
    name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=6)
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    token: str


# ── User ──

class UserResponse(BaseModel):
    id: UUID
    phone: str
    email: Optional[str]
    name: str
    role: UserRole
    verified: bool
    kyc_status: KYCStatus
    location: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    location: Optional[str] = None


# ── KYC ──

class KYCDocumentResponse(BaseModel):
    id: UUID
    doc_type: str
    doc_url: str
    status: DocStatus
    uploaded_at: datetime

    model_config = {"from_attributes": True}