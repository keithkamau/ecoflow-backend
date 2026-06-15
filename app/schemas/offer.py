from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.models.offer import OfferStatus


class OfferCreate(BaseModel):
    listing_id: int
    offered_price: float
    quantity: float
    note: Optional[str] = None

    @field_validator("offered_price", "quantity")
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("must be greater than zero")
        return v


class OfferUpdate(BaseModel):
    status: OfferStatus
    note: Optional[str] = None


class CounterOfferCreate(BaseModel):
    counter_price: float
    counter_quantity: Optional[float] = None
    counter_note: Optional[str] = None

    @field_validator("counter_price", "counter_quantity")
    def must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("must be greater than zero")
        return v


class OfferResponse(BaseModel):
    id: int
    listing_id: int
    recycler_id: int
    offered_price: float
    quantity: float
    status: OfferStatus
    note: Optional[str]
    counter_price: Optional[float]
    counter_quantity: Optional[float]
    counter_note: Optional[str]
    countered_at: Optional[datetime]
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
