from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.models.pickup import PickupStatus


class DriverInfo(BaseModel):
    id: int
    name: str
    phone: str
    vehicle: str
    license_plate: str


class PickupCreate(BaseModel):
    transaction_id: int
    scheduled_time: datetime
    pickup_address: Optional[str] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    notes: Optional[str] = None


class PickupUpdate(BaseModel):
    status: Optional[PickupStatus] = None
    actual_time: Optional[datetime] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    pickup_address: Optional[str] = None
    notes: Optional[str] = None


class PickupAssignDriver(BaseModel):
    driver_id: int


class PickupResponse(BaseModel):
    id: int
    transaction_id: int
    scheduled_time: datetime
    actual_time: Optional[datetime] = None
    status: PickupStatus
    driver_id: Optional[int] = None
    driver: Optional[DriverInfo] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    pickup_address: Optional[str] = None
    proof_url: Optional[str] = None
    weight: Optional[float] = None
    signature: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
