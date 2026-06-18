from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

from app.models.driver import DriverStatus


class DriverCreate(BaseModel):
    name: str
    phone: str
    vehicle: str
    license_plate: str


class DriverResponse(BaseModel):
    id: int
    name: str
    phone: str
    vehicle: str
    license_plate: str
    status: DriverStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
