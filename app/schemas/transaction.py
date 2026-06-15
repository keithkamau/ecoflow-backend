from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.transaction import TransactionStatus


class TransactionCreate(BaseModel):
    offer_id: int
    listing_id: int
    seller_id: int
    recycler_id: int
    agreed_price: float
    final_quantity: float
    final_price: float


class TransactionUpdate(BaseModel):
    status: TransactionStatus
    pickup_notes: Optional[str] = None
    dispute_reason: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    listing_id: int
    offer_id: int
    seller_id: int
    recycler_id: int
    agreed_price: float
    final_quantity: float
    final_price: float
    status: TransactionStatus
    pickup_notes: Optional[str]
    pickup_scheduled_at: Optional[datetime]
    disputed_at: Optional[datetime]
    dispute_reason: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
