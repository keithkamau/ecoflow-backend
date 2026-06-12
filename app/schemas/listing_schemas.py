# app/schemas/listing_schemas.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# Material Schemas 

class MaterialBase(BaseModel):
    type: str
    unit: str = "kg"
    reference_price: Optional[float] = None
    description: Optional[str] = None


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


#  ListingPhoto Schemas 

class ListingPhotoBase(BaseModel):
    photo_url: str


class ListingPhotoCreate(ListingPhotoBase):
    pass


class ListingPhotoResponse(ListingPhotoBase):
    id: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


#  Listing Schemas 

class ListingBase(BaseModel):
    material_id: int
    quantity: float = Field(gt=0)
    condition: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    price_expectation: Optional[float] = None
    preferred_pickup_start: Optional[datetime] = None
    preferred_pickup_end: Optional[datetime] = None


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    material_id: Optional[int] = None
    quantity: Optional[float] = Field(default=None, gt=0)
    condition: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    price_expectation: Optional[float] = None
    preferred_pickup_start: Optional[datetime] = None
    preferred_pickup_end: Optional[datetime] = None
    status: Optional[str] = None


class ListingResponse(ListingBase):
    id: int
    seller_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    material: Optional[MaterialResponse] = None
    photos: List[ListingPhotoResponse] = []

    model_config = {"from_attributes": True}


# Search & Filter Schemas

class ListingSearchFilters(BaseModel):
    material_type: Optional[str] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None
    status: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: Optional[float] = Field(default=None, gt=0)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class ListingSearchResponse(BaseModel):
    total: int
    listings: List[ListingResponse]


# Inventory Schemas 

class InventoryItem(BaseModel):
    material_type: str
    total_quantity: float
    total_spent: Optional[float] = None
    listing_count: int


class InventoryResponse(BaseModel):
    recycler_id: int
    items: List[InventoryItem]