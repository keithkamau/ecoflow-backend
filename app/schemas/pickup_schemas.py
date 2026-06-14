import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.pickup import PickupStatus, DriverStatus


# ── Location ────────────────────────────────────────────────────────────────

class LocationSchema(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    address: str


# ── Pickup ───────────────────────────────────────────────────────────────────

class PickupCreate(BaseModel):
    transaction_id: uuid.UUID
    scheduled_time: datetime
    pickup_location: LocationSchema
    notes: Optional[str] = None


class PickupUpdate(BaseModel):
    status: Optional[PickupStatus] = None
    actual_time: Optional[datetime] = None
    driver_id: Optional[uuid.UUID] = None
    notes: Optional[str] = None


class PickupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    transaction_id: uuid.UUID
    scheduled_time: datetime
    actual_time: Optional[datetime]
    pickup_location: dict
    status: PickupStatus
    driver_id: Optional[uuid.UUID]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# ── Driver ────────────────────────────────────────────────────────────────────

class DriverCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=7, max_length=20)
    vehicle: str
    license_plate: str


class DriverUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    vehicle: Optional[str] = None
    license_plate: Optional[str] = None
    status: Optional[DriverStatus] = None


class DriverResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recycler_id: uuid.UUID
    name: str
    phone: str
    vehicle: str
    license_plate: str
    status: DriverStatus
    created_at: datetime


# ── Proof of Pickup ───────────────────────────────────────────────────────────

VALID_MATERIAL_TYPES = {"plastic", "metal", "paper", "glass", "electronics", "rubber", "textile", "other"}


class ProofOfPickupCreate(BaseModel):
    weight: float = Field(..., gt=0, description="Weight in kilograms")
    material_type: str = Field(default="other")
    photos: List[str] = Field(default_factory=list, description="S3 photo URLs")
    driver_signature: Optional[str] = None
    notes: Optional[str] = None


class ProofOfPickupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pickup_id: uuid.UUID
    weight: float
    material_type: str
    photos: List[str]
    timestamp: datetime
    driver_signature: Optional[str]
    notes: Optional[str]
    created_at: datetime


# ── Distance / Nearby ─────────────────────────────────────────────────────────

class DistanceRequest(BaseModel):
    origin_lat: float = Field(..., ge=-90, le=90)
    origin_lng: float = Field(..., ge=-180, le=180)
    dest_lat: float = Field(..., ge=-90, le=90)
    dest_lng: float = Field(..., ge=-180, le=180)
    base_price: float = Field(default=0.0, ge=0)


class DistanceResponse(BaseModel):
    distance_km: float
    adjusted_price: float
    surcharge: float


class NearbyUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    full_name: Optional[str]
    role: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    distance_km: float


# ── Analytics ─────────────────────────────────────────────────────────────────

class EnvironmentalImpactResponse(BaseModel):
    total_weight_kg: float
    co2_saved_kg: float
    trees_equivalent: float
    total_pickups_completed: int
    material_breakdown: dict


class TransactionAnalyticsResponse(BaseModel):
    total_pickups: int
    completed: int
    pending: int
    in_progress: int
    cancelled: int
    period_days: int


class SellerPerformanceResponse(BaseModel):
    seller_id: str
    total_transactions: int
    total_weight_sold: float
    total_earnings: float
    avg_price_per_kg: float


class RecyclerAnalyticsResponse(BaseModel):
    recycler_id: str
    total_purchases: int
    total_weight_sourced: float
    total_spent: float
    top_materials: List[dict]
