from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    transaction_id: int
    user_id: int
    amount: float
    payment_method: PaymentMethod = PaymentMethod.MPESA
    phone_number: Optional[str] = None

    @field_validator("amount")
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("payment amount must be greater than zero")
        return v

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v is not None:
            cleaned = v.strip()
            if cleaned.startswith("+"):
                cleaned = cleaned[1:]
            if not cleaned.startswith("254"):
                cleaned = "254" + cleaned.lstrip("0")
            if not (cleaned.startswith("254") and len(cleaned) == 12):
                raise ValueError("phone must be a valid Kenyan number")
        return v


class PaymentCallback(BaseModel):
    Body: dict


class PaymentResponse(BaseModel):
    id: int
    transaction_id: int
    user_id: int
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    reference: Optional[str]
    mpesa_receipt: Optional[str]
    merchant_request_id: Optional[str]
    checkout_request_id: Optional[str]
    phone_number: Optional[str]
    commission_rate: float
    commission_amount: Optional[float]
    created_at: datetime
    paid_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
